# Zenodo DOI numbering and redirects

This note explains the different numbers that appear around a Zenodo archive, using `eyeling` as the example.

## The three important numbers

```text
581706557
```

This is the GitHub repository ID used by Zenodo's GitHub badge endpoint. It is not a DOI and not a Zenodo record number.

```text
10.5281/zenodo.19068086
```

This is the Zenodo **Concept DOI** for the project. A Concept DOI represents the whole evolving archive: all versions together.

```text
10.5281/zenodo.20123338
```

This is a Zenodo **Version DOI**. It identifies one exact archived release. In this case, it corresponds to the Zenodo record page:

```text
https://zenodo.org/records/20123338
```

## What happens when opening the Concept DOI

When opening:

```text
https://doi.org/10.5281/zenodo.19068086
```

the browser does not go directly to the final record page. The resolution chain is:

```text
https://doi.org/10.5281/zenodo.19068086
  302 → https://zenodo.org/doi/10.5281/zenodo.19068086

https://zenodo.org/doi/10.5281/zenodo.19068086
  302 → https://zenodo.org/records/20123338

https://zenodo.org/records/20123338
  200 OK
```

So `doi.org` first delegates the DOI to Zenodo. Then Zenodo resolves the Concept DOI to the latest version's record page.

## Why does `19068086` lead to `20123338`?

Because `19068086` is the all-versions Concept DOI. Zenodo makes Concept DOIs resolve to the latest version.

At the moment:

```text
Concept DOI:  10.5281/zenodo.19068086
Latest page:  https://zenodo.org/records/20123338
Version DOI:  10.5281/zenodo.20123338
```

If a newer version is published later, the Concept DOI can resolve to a different `/records/...` page.

## Which DOI should be used?

Use the **Concept DOI** when referring to the project as a whole:

```md
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19068086-blue.svg)](https://doi.org/10.5281/zenodo.19068086)
```

Use the **Version DOI** when referring to one exact archived release:

```md
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20123338-blue.svg)](https://doi.org/10.5281/zenodo.20123338)
```

## Quick rule

```text
Concept DOI = stable DOI for the project / all versions
Version DOI = stable DOI for one exact release
Record URL  = Zenodo page for one specific version
GitHub ID   = repository number used by Zenodo badges
```

For a README badge, the Concept DOI is usually the best choice, because it keeps pointing to the latest archived release of the project.
