import "dart:convert";

import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:http/http.dart" as http;

class HttpService {
  static final http.Client _client = http.Client();
  static final String backendUrl =
      ConfigService().getConfigValue(ConfigKey.backendUrl);
  static final String basicAuthKey =
      ConfigService().getConfigValue(ConfigKey.basicAuthKey);

  Future<http.Response> checkBackendHealth() {
    return http.get(
      Uri.parse("$backendUrl/health/ping"),
      headers: {"Authorization": "Basic $basicAuthKey=="},
    );
  }

  Future<http.Response> getSharedCases() {
    return http.get(
      Uri.parse("$backendUrl/shared/cases"),
      headers: {"Authorization": "Basic $basicAuthKey=="},
    );
  }

  Future<http.Response> getCases(String workshopId) {
    return http.get(
      Uri.parse("$backendUrl/$workshopId/cases"),
      headers: {"Authorization": "Basic $basicAuthKey=="},
    );
  }

  Future<http.Response> getCaseDetails(String workshopId, String caseId) {
    return http.get(
      Uri.parse("$backendUrl/$workshopId/cases/$caseId"),
      headers: {"Authorization": "Basic $basicAuthKey=="},
    );
  }

  Future<http.Response> addCase(
    String workshopId,
    Map<String, dynamic> requestBody,
  ) {
    return _client.post(
      Uri.parse("$backendUrl/$workshopId/cases"),
      headers: {
        "Authorization": "Basic $basicAuthKey==",
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: jsonEncode(requestBody),
    );
  }

  Future<http.Response> deleteCase(String workshopId, String caseId) {
    return http.delete(
      Uri.parse("$backendUrl/$workshopId/cases/$caseId"),
      headers: {"Authorization": "Basic $basicAuthKey=="},
    );
  }
}
