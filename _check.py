import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
suite = root if root.tag == "testsuite" else root[0]
total = int(suite.get("tests"))
failures = int(suite.get("failures"))
errors = int(suite.get("errors"))

failing = {
    tc.get("name") for tc in root.iter("testcase") if len(tc)
}

BASELINE = frozenset(
    [
        "test_finance_donation_lifecycle_and_summary",
        "test_liturgy_mass_schedules_and_intentions",
        "test_archive_indicator_documents_by_type_via_api",
        "test_survey_lifecycle_and_responses",
        "test_document_and_type_lifecycle",
        "test_governance_layer_crud",
        "test_sacramental_amendment_workflow",
        "test_forgot_password_returns_success_for_existing_user",
        "test_forgot_password_returns_success_for_unknown_email",
        "test_reset_password_with_valid_token",
        "test_reset_password_with_invalid_token",
        "test_reset_password_token_is_single_use",
        "test_refresh_rotates_and_revokes_old_refresh_token",
        "test_logout_revokes_access_and_refresh_family",
        "test_statistics_end_to_end",
        "test_statistic_indicator_endpoints",
        "test_new_apis_integration::test_survey_lifecycle_and_responses",
        "test_new_apis_integration::test_document_and_type_lifecycle",
        "test_new_apis_integration::test_governance_layer_crud",
        "test_new_apis_integration::test_sacramental_amendment_workflow",
        "test_password_reset::test_forgot_password_returns_success_for_existing_user",
        "test_password_reset::test_forgot_password_returns_success_for_unknown_email",
        "test_password_reset::test_reset_password_with_valid_token",
        "test_password_reset::test_reset_password_with_invalid_token",
        "test_password_reset::test_reset_password_token_is_single_use",
        "test_security_integration::test_refresh_rotates_and_revokes_old_refresh_token",
        "test_security_integration::test_logout_revokes_access_and_refresh_family",
        "test_statistics_integration::test_statistics_end_to_end",
        "test_statistics_integration::test_statistic_indicator_endpoints",
    ]
)

print(f"total={total} passed={total-failures-errors} failures={failures} errors={errors}")
print(f"failing_names={len(failing)}  baseline_names={len(BASELINE)}")
print(f"DIVERGENCE (newly failing or changed): {sorted(failing - BASELINE) or 'NONE'}")
print(f"identical_failure_set = {failing == BASELINE}")
