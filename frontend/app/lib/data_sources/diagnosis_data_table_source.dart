import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:flutter/material.dart";

const Map<DiagnosisStatus, IconData> diagnosisStatusIcons = {
  DiagnosisStatus.scheduled: Icons.schedule,
  DiagnosisStatus.action_required: Icons.warning,
  DiagnosisStatus.processing: Icons.autorenew,
  DiagnosisStatus.finished: Icons.done,
  DiagnosisStatus.failed: Icons.error,
};

class DiagnosisDataTableSource extends DataTableSource {
  DiagnosisDataTableSource({
    required this.diagnosisModels,
    required this.onPressedRow,
  });
  List<DiagnosisModel> diagnosisModels;
  final void Function(int) onPressedRow;

  Icon getStatusIcon(DiagnosisStatus? diagnosisStatus) {
    if (diagnosisStatus == null) return const Icon(Icons.question_mark);

    return Icon(diagnosisStatusIcons[diagnosisStatus]);
  }

  @override
  DataRow? getRow(int index) {
    final diagnosisModel = diagnosisModels[index];
    return DataRow(
      onSelectChanged: (_) => onPressedRow(index),
      cells: [
        DataCell(Center(child: getStatusIcon(diagnosisModel.status))),
        DataCell(Center(child: Text(diagnosisModel.caseId))),
        DataCell(
          Center(
            child: Text(
              diagnosisModel.timestamp.toGermanDateString(),
            ),
          ),
        ),
      ],
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => diagnosisModels.length;

  @override
  int get selectedRowCount => 0;
}
