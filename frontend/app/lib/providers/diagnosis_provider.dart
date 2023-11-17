import "dart:convert";

import "package:aw40_hub_frontend/dtos/diagnosis_dto.dart";
import "package:aw40_hub_frontend/models/case_model.dart";
import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/providers/case_provider.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:flutter/material.dart";
import "package:http/http.dart";
import "package:logging/logging.dart";

// ignore: prefer_mixin
class DiagnosisProvider with ChangeNotifier {
  DiagnosisProvider(this._httpService);
  final HttpService _httpService;

  final Logger _logger = Logger("diagnosis_provider");
  late String workShopId;
  List<DiagnosisModel> _diagnoses = [];

  // TODO maybe find another way of using the caseProvider than getting it iva param
  Future<List<DiagnosisModel>> getDiagnoses(CaseProvider caseProvider) async {
    final List<CaseModel> cases = await caseProvider.getCurrentCases();
    final List<String> caseIDs = cases.map((e) => e.id).toList();

    final List<Future<DiagnosisModel?>> individualDiagnosisRequests =
        caseIDs.map(getDiagnosis).toList();

    final List<DiagnosisModel?> diagnoses =
        await Future.wait(individualDiagnosisRequests);
    return _diagnoses = diagnoses
        .where((diagnosis) => diagnosis != null)
        .map((diagnosis) => diagnosis!)
        .toList();
  }

  Future<DiagnosisModel?> getDiagnosis(String caseId) async {
    final Response response =
        await _httpService.getDiagnosis(workShopId, caseId);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not get diagnosis. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return null;
    }

    final decodedJson = jsonDecode(response.body);
    if (decodedJson is! Map<String, dynamic>) return null;
    final Map<String, dynamic> body = decodedJson;
    final DiagnosisDto receivedDiagnosis = DiagnosisDto.fromJson(body);
    final DiagnosisModel diagnosisModel = receivedDiagnosis.toModel();
    return diagnosisModel;
  }

  Future<bool> startDiagnosis(String caseId) async {
    final Response response =
        await _httpService.startDiagnosis(workShopId, caseId);
    if (response.statusCode != 201) {
      _logger.warning(
        "Could not start diagnosis. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }

    notifyListeners();
    return true;
  }

  Future<bool> deleteDiagnosis(String caseId) async {
    final Response response =
        await _httpService.deleteDiagnosis(workShopId, caseId);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not delete diagnosis. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }

    // TODO adjust
    //_cases.removeWhere((caseModel) => caseModel.id == caseId);
    notifyListeners();
    return true;
  }
}
