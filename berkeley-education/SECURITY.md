# Security when reviewing archived notebooks

The original notebooks, README files, requirements and reports are preserved byte for byte for provenance. Their instructions describe historical experiments, not a supported secure runtime. Prefer inspecting recorded outputs and reports without running cells.

The sentiment project's compatibility file pins `transformers==4.30.2`, which has [published security advisories](https://github.com/advisories/GHSA-3863-2447-669p). The hate-speech notebook includes unpinned installation commands and mounts Google Drive; its exact original environment is not reproducibly locked.

For any rerun, review the code and installation cells first. Use a disposable VM or container with no credentials, personal files, private Drive mounts or production access. A Python virtual environment alone is not a security sandbox. Review and test patched dependencies in a separate working copy before adapting the research, and preserve the original artifacts and result labels.

Treat downloaded model artifacts and notebook code as executable inputs. Use trusted model/data sources and follow the [PyTorch security policy](https://github.com/pytorch/pytorch/security/policy) and [Transformers security policy](https://github.com/huggingface/transformers/security/policy). No model was retrained and no replacement environment was validated for this documentation update.

[Collection index](README.md) · [Import provenance](import-manifest.json)
