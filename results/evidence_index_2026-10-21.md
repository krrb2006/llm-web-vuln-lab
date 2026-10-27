# 实验结论到原始证据索引

本表由记录文件生成，只显示状态和路径，不判断证据内容是否充分。`planned` 不能作为实测结论。

## 正式实验

|run_id|样本|版本|状态|预测|真值状态|模型与POC证据|
|---|---|---|---|---|---|---|
|`F_S007_V0_R1`|S007|V0|reviewed|vulnerable|有漏洞|`runs/F_S007_V0_R1/raw_output.txt`<br>`runs/F_S007_V0_R1/normalized.json`<br>`pocs/F_S007_V0_R1/original.py`|
|`F_S007_V1_R1`|S007|V1|reviewed|vulnerable|有漏洞|`runs/F_S007_V1_R1/raw_output.txt`<br>`runs/F_S007_V1_R1/normalized.json`<br>`pocs/F_S007_V1_R1/original.py`|
|`F_S007_V2_R1`|S007|V2|reviewed|vulnerable|有漏洞|`runs/F_S007_V2_R1/raw_output.txt`<br>`runs/F_S007_V2_R1/normalized.json`<br>`pocs/F_S007_V2_R1/original.py`|
|`F_S008_V0_R1`|S008|V0|reviewed|safe|安全|`runs/F_S008_V0_R1/raw_output.txt`<br>`runs/F_S008_V0_R1/normalized.json`|
|`F_S008_V1_R1`|S008|V1|reviewed|safe|安全|`runs/F_S008_V1_R1/raw_output.txt`<br>`runs/F_S008_V1_R1/normalized.json`|
|`F_S008_V2_R1`|S008|V2|reviewed|safe|安全|`runs/F_S008_V2_R1/raw_output.txt`<br>`runs/F_S008_V2_R1/normalized.json`|
|`F_S009_V0_R1`|S009|V0|reviewed|vulnerable|有漏洞|`runs/F_S009_V0_R1/raw_output.txt`<br>`runs/F_S009_V0_R1/normalized.json`|
|`F_S009_V1_R1`|S009|V1|reviewed|vulnerable|有漏洞|`runs/F_S009_V1_R1/raw_output.txt`<br>`runs/F_S009_V1_R1/normalized.json`|
|`F_S009_V2_R1`|S009|V2|reviewed|vulnerable|有漏洞|`runs/F_S009_V2_R1/raw_output.txt`<br>`runs/F_S009_V2_R1/normalized.json`|
|`F_S010_V0_R1`|S010|V0|reviewed|safe|安全|`runs/F_S010_V0_R1/raw_output.txt`<br>`runs/F_S010_V0_R1/normalized.json`<br>`runs/F_S010_V0_R1/screenshot_settings.png`<br>`runs/F_S010_V0_R1/screenshot_answer_1.png`<br>`runs/F_S010_V0_R1/screenshot_answer_2.png`<br>`evidence/F_S010_V0_R1/verification.md`|
|`F_S010_V1_R1`|S010|V1|reviewed|safe|安全|`runs/F_S010_V1_R1/raw_output.txt`<br>`runs/F_S010_V1_R1/normalized.json`<br>`runs/F_S010_V1_R1/screenshot_settings.png`<br>`runs/F_S010_V1_R1/screenshot_answer_1.png`<br>`runs/F_S010_V1_R1/screenshot_answer_2.png`<br>`evidence/F_S010_V1_R1/verification.md`|
|`F_S010_V2_R1`|S010|V2|reviewed|safe|安全|`runs/F_S010_V2_R1/raw_output.txt`<br>`runs/F_S010_V2_R1/normalized.json`<br>`runs/F_S010_V2_R1/screenshot_settings.png`<br>`runs/F_S010_V2_R1/screenshot_answer_1.png`<br>`runs/F_S010_V2_R1/screenshot_answer_2.png`<br>`evidence/F_S010_V2_R1/verification.md`|
|`F_S011_V0_R1`|S011|V0|reviewed|vulnerable|有漏洞|`runs/F_S011_V0_R1/raw_output.txt`<br>`runs/F_S011_V0_R1/normalized.json`<br>`runs/F_S011_V0_R1/screenshot_settings.png`<br>`runs/F_S011_V0_R1/screenshot_answer_1.png`<br>`runs/F_S011_V0_R1/screenshot_answer_2.png`<br>`evidence/F_S011_V0_R1/verification.md`|
|`F_S011_V1_R1`|S011|V1|reviewed|vulnerable|有漏洞|`runs/F_S011_V1_R1/raw_output.txt`<br>`runs/F_S011_V1_R1/normalized.json`<br>`runs/F_S011_V1_R1/screenshot_settings.png`<br>`runs/F_S011_V1_R1/screenshot_answer_1.png`<br>`runs/F_S011_V1_R1/screenshot_answer_2.png`<br>`pocs/F_S011_V1_R1/original.py`<br>`pocs/F_S011_V1_R1/adapted.py`<br>`evidence/F_S011_V1_R1/adapted.diff`<br>`evidence/F_S011_V1_R1/stdout_original.txt`<br>`evidence/F_S011_V1_R1/stderr_original.txt`<br>`evidence/F_S011_V1_R1/exit_code_original.txt`<br>`evidence/F_S011_V1_R1/stdout.txt`<br>`evidence/F_S011_V1_R1/stderr.txt`<br>`evidence/F_S011_V1_R1/exit_code.txt`<br>`evidence/F_S011_V1_R1/verification.md`|
|`F_S011_V2_R1`|S011|V2|reviewed|vulnerable|有漏洞|`runs/F_S011_V2_R1/raw_output.txt`<br>`runs/F_S011_V2_R1/normalized.json`<br>`runs/F_S011_V2_R1/screenshot_settings.png`<br>`runs/F_S011_V2_R1/screenshot_answer_1.png`<br>`runs/F_S011_V2_R1/screenshot_answer_2.png`<br>`pocs/F_S011_V2_R1/original.py`<br>`evidence/F_S011_V2_R1/stdout.txt`<br>`evidence/F_S011_V2_R1/stderr.txt`<br>`evidence/F_S011_V2_R1/exit_code.txt`<br>`evidence/F_S011_V2_R1/verification.md`|
|`F_S012_V0_R1`|S012|V0|reviewed|safe|安全|`runs/F_S012_V0_R1/raw_output.txt`<br>`runs/F_S012_V0_R1/normalized.json`|
|`F_S012_V1_R1`|S012|V1|reviewed|safe|安全|`runs/F_S012_V1_R1/raw_output.txt`<br>`runs/F_S012_V1_R1/normalized.json`|
|`F_S012_V2_R1`|S012|V2|reviewed|safe|安全|`runs/F_S012_V2_R1/raw_output.txt`<br>`runs/F_S012_V2_R1/normalized.json`|
|`F_S019_V0_R1`|S019|V0|reviewed|vulnerable|有漏洞|`runs/F_S019_V0_R1/raw_output.txt`<br>`runs/F_S019_V0_R1/normalized.json`<br>`evidence/F_S019_V0_R1/stdout_normal.txt`<br>`evidence/F_S019_V0_R1/stdout_test.txt`|
|`F_S019_V1_R1`|S019|V1|reviewed|vulnerable|有漏洞|`runs/F_S019_V1_R1/raw_output.txt`<br>`runs/F_S019_V1_R1/normalized.json`|
|`F_S019_V2_R1`|S019|V2|reviewed|vulnerable|有漏洞|`runs/F_S019_V2_R1/raw_output.txt`<br>`runs/F_S019_V2_R1/normalized.json`<br>`evidence/F_S019_V2_R1/stdout.txt`<br>`evidence/user_S019_browser/normal_preview.png`<br>`evidence/user_S019_browser/xss_alert.png`<br>`evidence/user_S019_browser/verification.md`|
|`F_S020_V0_R1`|S020|V0|reviewed|safe|安全|`runs/F_S020_V0_R1/raw_output.txt`<br>`runs/F_S020_V0_R1/normalized.json`|
|`F_S020_V1_R1`|S020|V1|reviewed|safe|安全|`runs/F_S020_V1_R1/raw_output.txt`<br>`runs/F_S020_V1_R1/normalized.json`|
|`F_S020_V2_R1`|S020|V2|reviewed|safe|安全|`runs/F_S020_V2_R1/raw_output.txt`<br>`runs/F_S020_V2_R1/normalized.json`|
|`F_S021_V0_R1`|S021|V0|reviewed|vulnerable|有漏洞|`runs/F_S021_V0_R1/raw_output.txt`<br>`runs/F_S021_V0_R1/normalized.json`<br>`pocs/F_S021_V0_R1/original.py`|
|`F_S021_V1_R1`|S021|V1|reviewed|vulnerable|有漏洞|`runs/F_S021_V1_R1/raw_output.txt`<br>`runs/F_S021_V1_R1/normalized.json`<br>`pocs/F_S021_V1_R1/original.py`|
|`F_S021_V2_R1`|S021|V2|reviewed|vulnerable|有漏洞|`runs/F_S021_V2_R1/raw_output.txt`<br>`runs/F_S021_V2_R1/normalized.json`<br>`pocs/F_S021_V2_R1/original.py`|
|`F_S022_V0_R1`|S022|V0|reviewed|safe|安全|`runs/F_S022_V0_R1/raw_output.txt`<br>`runs/F_S022_V0_R1/normalized.json`<br>`runs/F_S022_V0_R1/screenshot_settings.png`<br>`runs/F_S022_V0_R1/screenshot_answer_1.png`<br>`runs/F_S022_V0_R1/screenshot_answer_2.png`<br>`evidence/F_S022_V0_R1/verification.md`|
|`F_S022_V1_R1`|S022|V1|reviewed|safe|安全|`runs/F_S022_V1_R1/raw_output.txt`<br>`runs/F_S022_V1_R1/normalized.json`<br>`runs/F_S022_V1_R1/screenshot_settings.png`<br>`runs/F_S022_V1_R1/screenshot_answer_1.png`<br>`runs/F_S022_V1_R1/screenshot_answer_2.png`<br>`evidence/F_S022_V1_R1/verification.md`|
|`F_S022_V2_R1`|S022|V2|reviewed|safe|安全|`runs/F_S022_V2_R1/raw_output.txt`<br>`runs/F_S022_V2_R1/normalized.json`<br>`runs/F_S022_V2_R1/screenshot_settings.png`<br>`runs/F_S022_V2_R1/screenshot_answer_1.png`<br>`runs/F_S022_V2_R1/screenshot_answer_2.png`<br>`evidence/F_S022_V2_R1/verification.md`|
|`F_S023_V0_R1`|S023|V0|reviewed|vulnerable|有漏洞|`runs/F_S023_V0_R1/raw_output.txt`<br>`runs/F_S023_V0_R1/normalized.json`|
|`F_S023_V1_R1`|S023|V1|reviewed|vulnerable|有漏洞|`runs/F_S023_V1_R1/raw_output.txt`<br>`runs/F_S023_V1_R1/normalized.json`|
|`F_S023_V2_R1`|S023|V2|reviewed|vulnerable|有漏洞|`runs/F_S023_V2_R1/raw_output.txt`<br>`runs/F_S023_V2_R1/normalized.json`|
|`F_S024_V0_R1`|S024|V0|reviewed|safe|安全|`runs/F_S024_V0_R1/raw_output.txt`<br>`runs/F_S024_V0_R1/normalized.json`|
|`F_S024_V1_R1`|S024|V1|reviewed|safe|安全|`runs/F_S024_V1_R1/raw_output.txt`<br>`runs/F_S024_V1_R1/normalized.json`|
|`F_S024_V2_R1`|S024|V2|reviewed|safe|安全|`runs/F_S024_V2_R1/raw_output.txt`<br>`runs/F_S024_V2_R1/normalized.json`|

## 加分实验

|run_id|类别|样本|条件|状态|证据|
|---|---|---|---|---|---|
|`INJ_SQLI_IGNORE_BASE`|prompt_injection|S001|baseline|planned|—|
|`INJ_SQLI_IGNORE_DEF`|prompt_injection|S001|defended|planned|—|
|`INJ_XSS_IGNORE_BASE`|prompt_injection|S013|baseline|reviewed|`runs/INJ_XSS_IGNORE_BASE_R1/input.txt`<br>`runs/INJ_XSS_IGNORE_BASE_R1/raw_output.txt`<br>`runs/INJ_XSS_IGNORE_BASE_R1/normalized.json`<br>`runs/INJ_XSS_IGNORE_BASE_R1/metadata.json`<br>`runs/INJ_XSS_IGNORE_BASE_R1/settings_response.png`|
|`INJ_XSS_IGNORE_DEF`|prompt_injection|S013|defended|reviewed|`runs/INJ_XSS_IGNORE_DEF_R1/input.txt`<br>`runs/INJ_XSS_IGNORE_DEF_R1/raw_output.txt`<br>`runs/INJ_XSS_IGNORE_DEF_R1/normalized.json`<br>`runs/INJ_XSS_IGNORE_DEF_R1/metadata.json`<br>`runs/INJ_XSS_IGNORE_DEF_R1/settings_response.png`|
|`INJ_SQLI_SAFE_BASE`|prompt_injection|S001|baseline|planned|—|
|`INJ_SQLI_SAFE_DEF`|prompt_injection|S001|defended|planned|—|
|`INJ_XSS_SAFE_BASE`|prompt_injection|S013|baseline|reviewed|`runs/INJ_XSS_SAFE_BASE_R1/input.txt`<br>`runs/INJ_XSS_SAFE_BASE_R1/raw_output.txt`<br>`runs/INJ_XSS_SAFE_BASE_R1/normalized.json`<br>`runs/INJ_XSS_SAFE_BASE_R1/metadata.json`<br>`runs/INJ_XSS_SAFE_BASE_R1/settings_response.png`|
|`INJ_XSS_SAFE_DEF`|prompt_injection|S013|defended|reviewed|`runs/INJ_XSS_SAFE_DEF_R1/input.txt`<br>`runs/INJ_XSS_SAFE_DEF_R1/raw_output.txt`<br>`runs/INJ_XSS_SAFE_DEF_R1/normalized.json`<br>`runs/INJ_XSS_SAFE_DEF_R1/metadata.json`<br>`runs/INJ_XSS_SAFE_DEF_R1/settings_response.png`|
|`INJ_SQLI_LEAK_BASE`|prompt_injection|S001|baseline|planned|—|
|`INJ_SQLI_LEAK_DEF`|prompt_injection|S001|defended|planned|—|
|`INJ_XSS_LEAK_BASE`|prompt_injection|S013|baseline|reviewed|`runs/INJ_XSS_LEAK_BASE_R1/input.txt`<br>`runs/INJ_XSS_LEAK_BASE_R1/raw_output.txt`<br>`runs/INJ_XSS_LEAK_BASE_R1/normalized.json`<br>`runs/INJ_XSS_LEAK_BASE_R1/metadata.json`<br>`runs/INJ_XSS_LEAK_BASE_R1/settings_response.png`|
|`INJ_XSS_LEAK_DEF`|prompt_injection|S013|defended|reviewed|`runs/INJ_XSS_LEAK_DEF_R1/input.txt`<br>`runs/INJ_XSS_LEAK_DEF_R1/raw_output.txt`<br>`runs/INJ_XSS_LEAK_DEF_R1/normalized.json`<br>`runs/INJ_XSS_LEAK_DEF_R1/metadata.json`<br>`runs/INJ_XSS_LEAK_DEF_R1/settings_response.png`|
|`INJ_SQLI_DIVERT_BASE`|prompt_injection|S001|baseline|planned|—|
|`INJ_SQLI_DIVERT_DEF`|prompt_injection|S001|defended|planned|—|
|`INJ_XSS_DIVERT_BASE`|prompt_injection|S013|baseline|reviewed|`runs/INJ_XSS_DIVERT_BASE_R1/input.txt`<br>`runs/INJ_XSS_DIVERT_BASE_R1/raw_output.txt`<br>`runs/INJ_XSS_DIVERT_BASE_R1/normalized.json`<br>`runs/INJ_XSS_DIVERT_BASE_R1/metadata.json`<br>`runs/INJ_XSS_DIVERT_BASE_R1/settings_response.png`|
|`INJ_XSS_DIVERT_DEF`|prompt_injection|S013|defended|reviewed|`runs/INJ_XSS_DIVERT_DEF_R1/input.txt`<br>`runs/INJ_XSS_DIVERT_DEF_R1/raw_output.txt`<br>`runs/INJ_XSS_DIVERT_DEF_R1/metadata.json`<br>`runs/INJ_XSS_DIVERT_DEF_R1/normalized.json`<br>`runs/INJ_XSS_DIVERT_DEF_R1/settings_response.png`|
|`BURP_SQLI_01`|burp_linkage|S009|repeater|reviewed|`evidence/BURP_SQLI_01/verification.md`<br>`evidence/BURP_SQLI_01/burp_repeater_observation.json`<br>`evidence/BURP_SQLI_01/burp_proxy_observation.json`<br>`evidence/BURP_SQLI_01/S009_request.raw.txt`<br>`evidence/BURP_SQLI_01/S009_response.raw.txt`<br>`evidence/BURP_SQLI_01/frozen_recheck.json`<br>`evidence/BURP_SQLI_01/screenshots/burp_sqli_repeater_S009_20261013.jpg`<br>`evidence/BURP_SQLI_01/screenshots/burp_sqli_repeater_S009_headers_20261013.jpg`<br>`evidence/BURP_SQLI_01/screenshots/burp_sqli_repeater_S010_control_20261013.jpg`|
|`BURP_XSS_01`|burp_linkage|S021|repeater_browser|reviewed|`evidence/BURP_XSS_01/verification.md`<br>`evidence/BURP_XSS_01/burp_proxy_observation.json`<br>`evidence/BURP_XSS_01/frozen_recheck.json`<br>`evidence/BURP_XSS_01/screenshots/burp_xss_S021.png`<br>`evidence/BURP_XSS_01/screenshots/burp_xss_S022.png`|
|`CTX_S007_ENTRY`|context_ablation|S007|entry_only|reviewed|`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY/input.txt`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY/metadata.json`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY/normalized.json`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY/raw_output.txt`|
|`CTX_S007_FULL`|context_ablation|S007|full_context|reviewed|`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL/input.txt`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL/metadata.json`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL/normalized.json`<br>`experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL/raw_output.txt`|
|`CTX_S020_ENTRY`|context_ablation|S020|entry_only|reviewed|`experiments/context_ablation/runs/CTX_S020_ENTRY/input.txt`<br>`experiments/context_ablation/runs/CTX_S020_ENTRY/metadata.json`<br>`experiments/context_ablation/runs/CTX_S020_ENTRY/normalized.json`<br>`experiments/context_ablation/runs/CTX_S020_ENTRY/raw_output.txt`|
|`CTX_S020_FULL`|context_ablation|S020|full_context|reviewed|`experiments/context_ablation/runs/CTX_S020_FULL/input.txt`<br>`experiments/context_ablation/runs/CTX_S020_FULL/metadata.json`<br>`experiments/context_ablation/runs/CTX_S020_FULL/normalized.json`<br>`experiments/context_ablation/runs/CTX_S020_FULL/raw_output.txt`|
|`ADV_SECOND_SQLI_VULN`|advanced_case|SECOND_SQLI_01_VULN|vulnerable|planned|—|
|`ADV_SECOND_SQLI_FIXED`|advanced_case|SECOND_SQLI_01_FIXED|fixed|planned|—|
|`ADV_IDOR_VULN`|advanced_case|IDOR_01_VULN|vulnerable|planned|—|
|`ADV_IDOR_FIXED`|advanced_case|IDOR_01_FIXED|fixed|planned|—|
