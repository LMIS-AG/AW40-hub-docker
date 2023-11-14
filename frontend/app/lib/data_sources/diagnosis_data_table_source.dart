import "dart:math";

import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:flutter/material.dart";

class DiagnosisDataTableSource extends DataTableSource {
  DiagnosisDataTableSource({
    required this.diagnosisModels,
    required this.onPressedRow,
  });
  List<DiagnosisModel> diagnosisModels;
  final void Function(int) onPressedRow;

  Icon getStatusIcon(DiagnosisStatus? diagnosisStatus) {
    if (diagnosisStatus == null) return const Icon(Icons.question_mark);
    switch (diagnosisStatus) {
      case DiagnosisStatus.scheduled:
        return const Icon(Icons.schedule);
      case DiagnosisStatus.action_required:
        return const Icon(Icons.warning);
      case DiagnosisStatus.processing:
        return const Icon(Icons.autorenew);
      case DiagnosisStatus.finished:
        return const Icon(Icons.done);
      case DiagnosisStatus.failed:
        return const Icon(Icons.error);
    }
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
