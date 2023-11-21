import "package:aw40_hub_frontend/utils/utils.dart";

class DiagnosisModel {
  DiagnosisModel({
    required this.id,
    required this.timestamp,
    required this.status,
    required this.caseId,
    required this.stateMachineLog,
    required this.todos,
  });

  String id;
  DateTime timestamp;
  DiagnosisStatus status;
  String caseId;
  List<dynamic> stateMachineLog;
  List<dynamic> todos;
}
