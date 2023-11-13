import "package:aw40_hub_frontend/services/services.dart";
import "package:flutter/material.dart";
import "package:http/http.dart";
import "package:logging/logging.dart";

// ignore: prefer_mixin
class DiagnosisProvider with ChangeNotifier {
  DiagnosisProvider(this._httpService);
  final HttpService _httpService;

  final Logger _logger = Logger("diagnosis_provider");
  late String workShopId;

  Future<bool> getDiagnosis(String caseId) async {
    final Response response =
        await _httpService.getDiagnosis(workShopId, caseId);
    if (response.statusCode != 200) {
      _logger.warning(
        "Could not get diagnosis. "
        "${response.statusCode}: ${response.reasonPhrase}",
      );
      return false;
    }

    // TODO adjust
    //final Map<String, dynamic> body = jsonDecode(response.body);
    //final CaseDto receivedCase = CaseDto.fromJson(body);
    //_cases.add(receivedCase.toModel());
    notifyListeners();
    return true;
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

    // TODO adjust
    //final Map<String, dynamic> body = jsonDecode(response.body);
    //final CaseDto receivedCase = CaseDto.fromJson(body);
    //_cases.add(receivedCase.toModel());
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
