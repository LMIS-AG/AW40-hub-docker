import "dart:async";
import "dart:convert";

import "package:aw40_hub_frontend/dtos/diagnosis_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/providers/auth_provider.dart";
import "package:aw40_hub_frontend/services/helper_service.dart";
import "package:aw40_hub_frontend/services/http_service.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:flutter/material.dart";
import "package:http/http.dart";
import "package:logging/logging.dart";

class DiagnosisProvider with ChangeNotifier {
  DiagnosisProvider(this._httpService);

  final HttpService _httpService;

  final Logger _logger = Logger("diagnosis_provider");
  late final String workshopId;
  String? _authToken;

  /// The caseId of the diagnosis whose detail view was last shown.
  late String diagnosisCaseId;

  Future<List<DiagnosisModel>> getDiagnoses() async {
    final String authToken = _getAuthToken();
    final Response response =
        await _httpService.getDiagnoses(authToken, workshopId);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not get diagnoses. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return [];
    }
    final json = jsonDecode(response.body);
    if (json is! List) {
      _logger.warning("Could not decode json response to List.");
      return [];
    }
    return json.map((e) => DiagnosisDto.fromJson(e).toModel()).toList();
  }

  Future<DiagnosisModel?> getDiagnosis(String caseId) async {
    final String authToken = _getAuthToken();
    final Response response =
        await _httpService.getDiagnosis(authToken, workshopId, caseId);
    if (response.statusCode == 404) return null;
    final bool verifyStatusCode = HelperService.verifyStatusCode(
      response.statusCode,
      200,
      "Could not get diagnosis. ",
      response,
      _logger,
    );
    if (!verifyStatusCode) return null;
    return _decodeDiagnosisModelFromResponseBody(response);
  }

  Future<DiagnosisModel?> startDiagnosis(String caseId) async {
    final String authToken = _getAuthToken();
    final Response response =
        await _httpService.startDiagnosis(authToken, workshopId, caseId);
    final bool verifyStatusCode = HelperService.verifyStatusCode(
      response.statusCode,
      201,
      "Could not start diagnosis. ",
      response,
      _logger,
    );
    if (!verifyStatusCode) return null;
    notifyListeners();
    return _decodeDiagnosisModelFromResponseBody(response);
  }

  Future<bool> deleteDiagnosis(String caseId) async {
    final String authToken = _getAuthToken();
    final Response response =
        await _httpService.deleteDiagnosis(authToken, workshopId, caseId);
    final bool verifyStatusCode = HelperService.verifyStatusCode(
      response.statusCode,
      200,
      "Could not delete diagnosis. ",
      response,
      _logger,
    );
    if (!verifyStatusCode) return false;
    notifyListeners();
    return true;
  }

  DiagnosisModel? _decodeDiagnosisModelFromResponseBody(Response response) {
    final decodedJson = jsonDecode(response.body);
    if (decodedJson is! Map<String, dynamic>) return null;
    final Map<String, dynamic> body = decodedJson;
    final DiagnosisDto diagnosisDto = DiagnosisDto.fromJson(body);
    return diagnosisDto.toModel();
  }

  Future<void> fetchAndSetAuthToken(AuthProvider authProvider) async {
    _authToken = await authProvider.getAuthToken();
    notifyListeners();
  }

  String _getAuthToken() {
    final String? authToken = _authToken;
    if (authToken == null) {
      throw AppException(
        exceptionMessage: "Called DiagnosisProvider without auth token.",
        exceptionType: ExceptionType.unexpectedNullValue,
      );
    }
    return authToken;
  }
}
