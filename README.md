# ISAAC AI-Ready Records

## What this repo is
This repository serves as the single source of truth for ISAAC AI-ready scientific records. It defines the standardized structure and semantics required to make scientific data consistent, machine-readable, and ready for AI integration. The repository contains formal validation definitions, concrete record examples, and detailed usage documentation. All files are treated as concrete records to ensure immediate applicability in data workflows.

## Repository structure
- `schema/`: JSON definitions for validating record structure and content.
- `examples/`: Concrete JSON record examples demonstrating various scientific use cases.
- `wiki/`: Detailed documentation on record semantics and field definitions.

## Record contract (v1.0)
The following fields define the structure of a valid ISAAC record.

### Required
- `isaac_record_version`
- `record_id`
- `record_type`
- `timestamps`
- `sample`
- `measurement`
- `descriptors`

### Optional
- `acquisition_source`
- `context`
- `links`

## Roadmap (next)
- Add "derived" and "calculation" record examples
- Add validator/CI
