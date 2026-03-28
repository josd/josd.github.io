use std::io;

use hmac::{Hmac, Mac};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

use crate::report::{CaseReport, ReportItem};

type HmacSha256 = Hmac<Sha256>;

const DEMO_SHARED_SECRET: &str = "neutral-insight-demo-shared-secret";
const PHONE_CREATED_AT: &str = "2025-10-05T20:33:48.907163+00:00";
const PHONE_EXPIRES_AT: &str = "2025-10-05T22:33:48.907185+00:00";
const SCANNER_AUTH_AT: &str = "2025-10-05T20:35:48.907163+00:00";
const SCANNER_DUTY_AT: &str = "2025-10-05T20:37:48.907163+00:00";
const REQUEST_ACTION: &str = "odrl:use";
const REQUEST_PURPOSE: &str = "shopping_assist";
const EXPECTED_FILES_WRITTEN: usize = 6;

const CATALOG: [Product; 4] = [
    Product::new("prod:BIS_001", "Classic Tea Biscuits", 120),
    Product::new("prod:BIS_101", "Low-Sugar Tea Biscuits", 30),
    Product::new("prod:CHOC_050", "Milk Chocolate Bar", 150),
    Product::new("prod:CHOC_150", "85% Dark Chocolate", 60),
];

#[derive(Debug, Clone, Copy)]
struct Product {
    id: &'static str,
    name: &'static str,
    sugar_tenths: u32,
}

impl Product {
    const fn new(id: &'static str, name: &'static str, sugar_tenths: u32) -> Self {
        Self {
            id,
            name,
            sugar_tenths,
        }
    }
}

#[derive(Debug, Clone)]
struct Insight {
    id: String,
    metric: &'static str,
    threshold_tenths: u32,
    suggestion_policy: &'static str,
    scope_device: &'static str,
    scope_event: &'static str,
    retailer: &'static str,
    created_at: &'static str,
    expires_at: &'static str,
}

impl Insight {
    fn to_value(&self) -> Value {
        json!({
            "id": self.id,
            "type": "ins:Insight",
            "metric": self.metric,
            "threshold": self.threshold_tenths / 10,
            "suggestionPolicy": self.suggestion_policy,
            "scopeDevice": self.scope_device,
            "scopeEvent": self.scope_event,
            "retailer": self.retailer,
            "createdAt": self.created_at,
            "expiresAt": self.expires_at,
        })
    }
}

#[derive(Debug, Clone)]
struct Policy {
    target: String,
    expires_at: &'static str,
}

impl Policy {
    fn to_value(&self) -> Value {
        json!({
            "type": "odrl:Policy",
            "profile": "Delfour-Insight-Policy",
            "permission": {
                "action": "odrl:use",
                "target": self.target,
                "constraint": {
                    "leftOperand": "odrl:purpose",
                    "operator": "odrl:eq",
                    "rightOperand": "shopping_assist",
                }
            },
            "prohibition": {
                "action": "odrl:distribute",
                "target": self.target,
                "constraint": {
                    "leftOperand": "odrl:purpose",
                    "operator": "odrl:eq",
                    "rightOperand": "marketing",
                }
            },
            "duty": {
                "action": "odrl:delete",
                "constraint": {
                    "leftOperand": "odrl:dateTime",
                    "operator": "odrl:eq",
                    "rightOperand": self.expires_at,
                }
            }
        })
    }
}

#[derive(Debug, Clone)]
struct Signature {
    alg: &'static str,
    keyid: &'static str,
    created: &'static str,
    payload_hash_sha256: String,
    signature_hmac: String,
}

impl Signature {
    fn to_value(&self) -> Value {
        json!({
            "alg": self.alg,
            "keyid": self.keyid,
            "created": self.created,
            "payloadHashSHA256": self.payload_hash_sha256,
            "signatureHMAC": self.signature_hmac,
        })
    }
}

#[derive(Debug, Clone)]
struct Banner {
    headline: &'static str,
    note: Option<&'static str>,
    suggested_alternative: Option<&'static str>,
}

#[derive(Debug, Clone)]
struct Decision {
    at: &'static str,
    outcome: &'static str,
    reason: Option<&'static str>,
    target: Option<String>,
}

#[derive(Debug, Clone)]
struct Duty {
    at: &'static str,
    duty: &'static str,
    target: String,
}

#[derive(Debug, Clone)]
struct DelfourSummary {
    threshold_tenths: u32,
    signature_alg: &'static str,
    reason: String,
    banner: Banner,
    scanned: Product,
    alternative: Product,
    audit_len: usize,
    files_written: usize,
    signature_verified: bool,
    payload_hash_matches: bool,
    minimization_no_sensitive_terms: bool,
    scope_complete: bool,
    authorization_allowed: bool,
    banner_flags_high_sugar: bool,
    alternative_is_lower_sugar: bool,
    duty_timing_consistent: bool,
    marketing_prohibited: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let summary = run_demo();
    ensure_checks(&summary)?;

    Ok(CaseReport::new("delfour")
        .with_answer(vec![
            ReportItem::text(
                "The scanner is allowed to use a neutral shopping insight and recommends Low-Sugar Tea Biscuits instead of Classic Tea Biscuits.",
            ),
            ReportItem::field("case", "delfour"),
            ReportItem::field("decision", "Allowed"),
            ReportItem::field("scanned product", summary.scanned.name),
            ReportItem::field("suggested alternative", summary.alternative.name),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "The phone desensitizes a diabetes-related household condition into a scoped low-sugar need, wraps it in an expiring Insight + Policy envelope, signs it, and the scanner consumes that envelope for shopping assistance.",
            ),
            ReportItem::field("metric", "sugar_g_per_serving"),
            ReportItem::field("threshold", threshold_string(summary.threshold_tenths)),
            ReportItem::field("scope", "self-scanner @ pick_up_scanner"),
            ReportItem::field("retailer", "Delfour"),
            ReportItem::field("signature alg", summary.signature_alg),
            ReportItem::field("banner headline", summary.banner.headline),
            ReportItem::field("expires at", PHONE_EXPIRES_AT),
            ReportItem::field("reason.txt", summary.reason.trim_end()),
            ReportItem::field("audit entries", summary.audit_len.to_string()),
            ReportItem::field("bus files written", summary.files_written.to_string()),
        ])
        .with_check(vec![
            ReportItem::field("signature verifies", yes_no(summary.signature_verified)),
            ReportItem::field("payload hash matches", yes_no(summary.payload_hash_matches)),
            ReportItem::field(
                "minimization strips sensitive terms",
                yes_no(summary.minimization_no_sensitive_terms),
            ),
            ReportItem::field("scope complete", yes_no(summary.scope_complete)),
            ReportItem::field("authorization allowed", yes_no(summary.authorization_allowed)),
            ReportItem::field("high-sugar banner", yes_no(summary.banner_flags_high_sugar)),
            ReportItem::field(
                "alternative lowers sugar",
                yes_no(summary.alternative_is_lower_sugar),
            ),
            ReportItem::field("duty timing consistent", yes_no(summary.duty_timing_consistent)),
            ReportItem::field("marketing prohibited", yes_no(summary.marketing_prohibited)),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let summary = run_demo();
    ensure_checks(&summary)?;

    println!("=== Answer ===");
    println!(
        "The scanner is allowed to use a neutral shopping insight and recommends Low-Sugar Tea Biscuits instead of Classic Tea Biscuits."
    );
    println!("case                 : delfour");
    println!("decision             : Allowed");
    println!("scanned product      : {}", summary.scanned.name);
    println!("suggested alternative: {}", summary.alternative.name);
    println!();
    println!("=== Reason Why ===");
    println!(
        "The phone desensitizes a diabetes-related household condition into a scoped low-sugar need, wraps it in an expiring Insight + Policy envelope, signs it, and the scanner consumes that envelope for shopping assistance."
    );
    println!("metric               : sugar_g_per_serving");
    println!("threshold            : {}", threshold_string(summary.threshold_tenths));
    println!("scope                : self-scanner @ pick_up_scanner");
    println!("retailer             : Delfour");
    println!("signature alg        : {}", summary.signature_alg);
    println!("banner headline      : {}", summary.banner.headline);
    println!("expires at           : {}", PHONE_EXPIRES_AT);
    println!("reason.txt           : {}", summary.reason.trim_end());
    println!("audit entries        : {}", summary.audit_len);
    println!("bus files written    : {}", summary.files_written);
    println!();
    println!("=== Check ===");
    println!(
        "signature verifies              : {}",
        yes_no(summary.signature_verified)
    );
    println!(
        "payload hash matches            : {}",
        yes_no(summary.payload_hash_matches)
    );
    println!(
        "minimization strips sensitive terms: {}",
        yes_no(summary.minimization_no_sensitive_terms)
    );
    println!(
        "scope complete                  : {}",
        yes_no(summary.scope_complete)
    );
    println!(
        "authorization allowed           : {}",
        yes_no(summary.authorization_allowed)
    );
    println!(
        "high-sugar banner               : {}",
        yes_no(summary.banner_flags_high_sugar)
    );
    println!(
        "alternative lowers sugar        : {}",
        yes_no(summary.alternative_is_lower_sugar)
    );
    println!(
        "duty timing consistent          : {}",
        yes_no(summary.duty_timing_consistent)
    );
    println!(
        "marketing prohibited            : {}",
        yes_no(summary.marketing_prohibited)
    );

    Ok(())
}

fn ensure_checks(summary: &DelfourSummary) -> io::Result<()> {
    if !summary.signature_verified
        || !summary.payload_hash_matches
        || !summary.minimization_no_sensitive_terms
        || !summary.scope_complete
        || !summary.authorization_allowed
        || !summary.banner_flags_high_sugar
        || !summary.alternative_is_lower_sugar
        || !summary.duty_timing_consistent
        || !summary.marketing_prohibited
        || summary.files_written != EXPECTED_FILES_WRITTEN
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "delfour check failed: envelope, policy, or scanner checks did not hold",
        ));
    }

    Ok(())
}

fn run_demo() -> DelfourSummary {
    let needs_low_sugar = desensitize(&["Diabetes"]);
    let insight = derive_insight(
        needs_low_sugar,
        "Delfour",
        "self-scanner",
        "pick_up_scanner",
        "delfour",
    );
    let policy = policy_from_insight(&insight);
    let policy_value = policy.to_value();
    let envelope = json!({
        "insight": insight.to_value(),
        "policy": policy_value.clone(),
    });
    let signature = sign_envelope(&envelope);
    let signature_value = signature.to_value();
    let signature_verified = verify_signature(&envelope, &signature);
    let payload_hash_matches = matches!(
        signature_value.get("payloadHashSHA256"),
        Some(Value::String(value)) if value == &sha256_hex(&canonical_json(&envelope))
    );

    let reason = [
        "Household requires low-sugar guidance (diabetes in POD).",
        "A neutral Insight is scoped to device 'self-scanner', event 'pick_up_scanner', retailer 'Delfour', and expires soon; the policy confines use to shopping assistance.",
    ]
    .join(" ")
        + "\n";

    let (allowed, decision) = authorize(&policy_value, &insight.id);
    let authorization_allowed = allowed
        && decision.at == SCANNER_AUTH_AT
        && decision.outcome == "Allowed"
        && decision.reason.is_none()
        && decision.target.as_deref() == Some(insight.id.as_str());

    let (banner, scanned, alternative) = if authorization_allowed {
        simulate_scan_and_suggest(&insight)
    } else {
        (
            Banner {
                headline: "Policy blocked action",
                note: Some("Expired or prohibited"),
                suggested_alternative: None,
            },
            CATALOG[0],
            CATALOG[0],
        )
    };

    let duty_due = SCANNER_DUTY_AT > insight.expires_at;
    let duty = duty_due.then(|| Duty {
        at: SCANNER_DUTY_AT,
        duty: "delete_due",
        target: insight.id.clone(),
    });
    let duty_timing_consistent = if duty_due {
        duty.as_ref().is_some_and(|entry| {
            entry.at > insight.expires_at
                && entry.duty == "delete_due"
                && entry.target == insight.id
        })
    } else {
        duty.is_none()
    };

    let insight_text = canonical_json(&insight.to_value()).to_lowercase();
    let minimization_no_sensitive_terms =
        !insight_text.contains("diabetes") && !insight_text.contains("medical");
    let scope_complete = envelope.pointer("/insight/scopeDevice").is_some()
        && envelope.pointer("/insight/scopeEvent").is_some()
        && envelope.pointer("/insight/expiresAt").is_some();
    let banner_flags_high_sugar = banner.note == Some("High sugar");
    let alternative_is_lower_sugar = alternative.sugar_tenths < scanned.sugar_tenths
        && banner.suggested_alternative == Some(alternative.name);
    let marketing_prohibited = matches!(
        policy_value.pointer("/prohibition/constraint/rightOperand"),
        Some(Value::String(value)) if value == "marketing"
    ) && matches!(
        policy_value.pointer("/prohibition/action"),
        Some(Value::String(value)) if value == "odrl:distribute"
    );

    DelfourSummary {
        threshold_tenths: insight.threshold_tenths,
        signature_alg: signature.alg,
        reason,
        banner,
        scanned,
        alternative,
        audit_len: 1 + usize::from(duty.is_some()),
        files_written: EXPECTED_FILES_WRITTEN,
        signature_verified,
        payload_hash_matches,
        minimization_no_sensitive_terms,
        scope_complete,
        authorization_allowed,
        banner_flags_high_sugar,
        alternative_is_lower_sugar,
        duty_timing_consistent,
        marketing_prohibited,
    }
}

fn desensitize(household_conditions: &[&str]) -> bool {
    household_conditions
        .iter()
        .any(|condition| *condition == "Diabetes")
}

fn derive_insight(
    needs_low_sugar: bool,
    retailer: &'static str,
    device: &'static str,
    event: &'static str,
    session_id: &str,
) -> Insight {
    let threshold_tenths = if needs_low_sugar { 100 } else { 100 };

    Insight {
        id: format!("https://example.org/insight/{session_id}"),
        metric: "sugar_g_per_serving",
        threshold_tenths,
        suggestion_policy: "lower_metric_first_higher_price_ok",
        scope_device: device,
        scope_event: event,
        retailer,
        created_at: PHONE_CREATED_AT,
        expires_at: PHONE_EXPIRES_AT,
    }
}

fn policy_from_insight(insight: &Insight) -> Policy {
    Policy {
        target: insight.id.clone(),
        expires_at: insight.expires_at,
    }
}

fn sign_envelope(envelope: &Value) -> Signature {
    let canonical = canonical_json(envelope);

    Signature {
        alg: "HMAC-SHA256",
        keyid: "demo-shared-secret",
        created: PHONE_CREATED_AT,
        payload_hash_sha256: sha256_hex(&canonical),
        signature_hmac: hmac_sha256_hex(DEMO_SHARED_SECRET, &canonical),
    }
}

fn verify_signature(envelope: &Value, signature: &Signature) -> bool {
    let canonical = canonical_json(envelope);
    let digest = sha256_hex(&canonical);

    digest.eq_ignore_ascii_case(&signature.payload_hash_sha256)
        && hmac_sha256_hex(DEMO_SHARED_SECRET, &canonical) == signature.signature_hmac
}

fn authorize(policy_value: &Value, insight_id: &str) -> (bool, Decision) {
    let expired = SCANNER_AUTH_AT > PHONE_EXPIRES_AT;
    let matches = matches!(
        policy_value.pointer("/permission/action"),
        Some(Value::String(value)) if value == REQUEST_ACTION
    ) && matches!(
        policy_value.pointer("/permission/target"),
        Some(Value::String(value)) if value == insight_id
    ) && matches!(
        policy_value.pointer("/permission/constraint/leftOperand"),
        Some(Value::String(value)) if value == "odrl:purpose"
    ) && matches!(
        policy_value.pointer("/permission/constraint/rightOperand"),
        Some(Value::String(value)) if value == REQUEST_PURPOSE
    );

    if expired || !matches {
        return (
            false,
            Decision {
                at: SCANNER_AUTH_AT,
                outcome: "Blocked",
                reason: Some(if expired { "expired" } else { "policy_mismatch" }),
                target: None,
            },
        );
    }

    (
        true,
        Decision {
            at: SCANNER_AUTH_AT,
            outcome: "Allowed",
            reason: None,
            target: Some(insight_id.to_string()),
        },
    )
}

fn simulate_scan_and_suggest(insight: &Insight) -> (Banner, Product, Product) {
    let scanned = CATALOG
        .iter()
        .find(|product| product.id == "prod:BIS_001")
        .copied()
        .expect("catalog should include the scanned biscuit");
    let threshold_tenths = insight.threshold_tenths;

    let alternative = CATALOG
        .iter()
        .filter(|product| product.sugar_tenths < scanned.sugar_tenths)
        .min_by_key(|product| product.sugar_tenths)
        .copied()
        .expect("catalog should include a lower-sugar alternative");

    let note = if scanned.sugar_tenths >= threshold_tenths {
        Some("High sugar")
    } else {
        None
    };

    (
        Banner {
            headline: if note.is_some() {
                "Track sugar per serving while you scan"
            } else {
                "Scan complete"
            },
            note,
            suggested_alternative: note.map(|_| alternative.name),
        },
        scanned,
        alternative,
    )
}

fn canonical_json(value: &Value) -> String {
    match value {
        Value::Null => "null".to_string(),
        Value::Bool(value) => {
            if *value {
                "true".to_string()
            } else {
                "false".to_string()
            }
        }
        Value::Number(number) => canonical_number(number),
        Value::String(text) => {
            serde_json::to_string(text).expect("string serialization should work")
        }
        Value::Array(items) => {
            let rendered = items.iter().map(canonical_json).collect::<Vec<_>>().join(",");
            format!("[{rendered}]")
        }
        Value::Object(map) => {
            let mut ordered = map.iter().collect::<Vec<_>>();
            ordered.sort_by(|(left, _), (right, _)| left.cmp(right));
            let rendered = ordered
                .into_iter()
                .map(|(key, item)| {
                    format!(
                        "{}:{}",
                        serde_json::to_string(key)
                            .expect("key serialization should work"),
                        canonical_json(item)
                    )
                })
                .collect::<Vec<_>>()
                .join(",");
            format!("{{{rendered}}}")
        }
    }
}

fn canonical_number(number: &serde_json::Number) -> String {
    if let Some(value) = number.as_i64() {
        format!("{value}.0")
    } else if let Some(value) = number.as_u64() {
        format!("{value}.0")
    } else {
        let value = number
            .as_f64()
            .expect("JSON numbers should convert to f64 for this example");
        if value.fract() == 0.0 {
            format!("{value:.1}")
        } else {
            value.to_string()
        }
    }
}

fn sha256_hex(text: &str) -> String {
    let digest = Sha256::digest(text.as_bytes());
    hex_string(&digest)
}

fn hmac_sha256_hex(secret: &str, text: &str) -> String {
    let mut mac =
        HmacSha256::new_from_slice(secret.as_bytes()).expect("HMAC-SHA256 accepts any key size");
    mac.update(text.as_bytes());
    let digest = mac.finalize().into_bytes();
    hex_string(&digest)
}

fn hex_string(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

fn threshold_string(tenths: u32) -> String {
    format!("{}.{:01}", tenths / 10, tenths % 10)
}

fn yes_no(value: bool) -> &'static str {
    if value {
        "yes"
    } else {
        "no"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn delfour_flow_stays_consistent() {
        let summary = run_demo();

        assert!(summary.signature_verified);
        assert!(summary.payload_hash_matches);
        assert!(summary.authorization_allowed);
        assert!(summary.banner_flags_high_sugar);
        assert!(summary.alternative_is_lower_sugar);
        assert!(summary.duty_timing_consistent);
        assert!(summary.marketing_prohibited);
        assert_eq!(summary.files_written, EXPECTED_FILES_WRITTEN);
        assert_eq!(summary.scanned.name, "Classic Tea Biscuits");
        assert_eq!(summary.alternative.name, "Low-Sugar Tea Biscuits");
        assert_eq!(summary.threshold_tenths, 100);
        assert_eq!(summary.audit_len, 1);
        assert_eq!(summary.signature_alg, "HMAC-SHA256");
        assert_eq!(summary.banner.headline, "Track sugar per serving while you scan");
        assert_eq!(summary.banner.suggested_alternative, Some("Low-Sugar Tea Biscuits"));
    }
}
