import "package:aw40_hub_frontend/models/diagnosis_model.dart";
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

  Future<List<DiagnosisModel>> getDiagnoses(List<String> caseIDs) async {
    // TODO implement (call getDiagnosis for each caseId)

    // mock data
    final List<DiagnosisModel> mockData = [
      DiagnosisModel(
        id: "1",
        timestamp: DateTime.now(),
        status: DiagnosisStatus.scheduled,
        caseId: "ABC123",
        stateMachineLog: ["Step 1", "Step 2"],
        todos: ["Task 1", "Task 2"],
      ),
      DiagnosisModel(
        id: "2",
        timestamp: DateTime.now(),
        status: DiagnosisStatus.finished,
        caseId: "XYZ789",
        stateMachineLog: ["Step 1", "Step 2", "Step 3"],
        todos: ["Task 1", "Task 2", "Task 3"],
      ),
      DiagnosisModel(
        id: "3",
        timestamp: DateTime.now(),
        status: DiagnosisStatus.processing,
        caseId: "DEF456",
        stateMachineLog: ["Step 1"],
        todos: ["Task 1"],
      ),
    ];

    return mockData;
  }

// TODO adjust return type
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

    // TODO adjust
    //final Map<String, dynamic> body = jsonDecode(response.body);
    //final CaseDto receivedCase = CaseDto.fromJson(body);
    //_cases.add(receivedCase.toModel());
    notifyListeners();

    // mock data
    return DiagnosisModel(
      id: "2",
      timestamp: DateTime.now(),
      status: DiagnosisStatus.finished,
      caseId: "XYZ789",
      stateMachineLog: ["Step 1", "Step 2", "Step 3"],
      todos: ["Task 1", "Task 2", "Task 3"],
    );
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
