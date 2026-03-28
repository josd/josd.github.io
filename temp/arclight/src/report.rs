use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CaseReport {
    pub case: String,
    pub answer: Vec<ReportItem>,
    pub reason_why: Vec<ReportItem>,
    pub check: Vec<ReportItem>,
}

impl CaseReport {
    pub fn new(case: impl Into<String>) -> Self {
        Self {
            case: case.into(),
            answer: Vec::new(),
            reason_why: Vec::new(),
            check: Vec::new(),
        }
    }

    pub fn with_answer(mut self, items: Vec<ReportItem>) -> Self {
        self.answer = items;
        self
    }

    pub fn with_reason_why(mut self, items: Vec<ReportItem>) -> Self {
        self.reason_why = items;
        self
    }

    pub fn with_check(mut self, items: Vec<ReportItem>) -> Self {
        self.check = items;
        self
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ReportItem {
    Text { text: String },
    Field { label: String, value: String },
}

impl ReportItem {
    pub fn text(text: impl Into<String>) -> Self {
        Self::Text { text: text.into() }
    }

    pub fn field(label: impl Into<String>, value: impl Into<String>) -> Self {
        Self::Field {
            label: label.into(),
            value: value.into(),
        }
    }
}
