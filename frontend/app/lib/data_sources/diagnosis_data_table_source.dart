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
  final rng = Random(); // TODO remove?
  final void Function(int) onPressedRow;

  Icon getStatusIcon(DiagnosisStatus? diagnosisStatus) {
    if (diagnosisStatus == null) return const Icon(Icons.question_mark);
    // TODO switch diagnosisStatus
    return const Icon(Icons.done);
  }

  @override
  DataRow? getRow(int index) {
    final diagnosisModel = diagnosisModels[index];
    return DataRow(
      onSelectChanged: (_) => onPressedRow(index),
      cells: [
        DataCell(getStatusIcon(diagnosisModel.status)),
        DataCell(Text(diagnosisModel.caseId)),
        DataCell(
          Text(
            diagnosisModel.timestamp.toGermanDateString(),
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
