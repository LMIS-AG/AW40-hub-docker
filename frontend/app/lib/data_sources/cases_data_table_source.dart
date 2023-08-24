import "dart:math";

import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:flutter/material.dart";

class CasesDataTableSource extends DataTableSource {
  CasesDataTableSource({required this.caseModels, required this.onPressedRow});
  List<CaseModel> caseModels;
  final rng = Random();
  final void Function(int) onPressedRow;

  Icon getStatusIcon(CaseStatus? caseStatus) {
    if (caseStatus == null) return const Icon(Icons.question_mark);
    return caseStatus == CaseStatus.closed
        ? const Icon(Icons.done)
        : const Icon(Icons.cached);
  }

  @override
  DataRow? getRow(int index) {
    final caseModel = caseModels[index];
    return DataRow(
      onSelectChanged: (_) => onPressedRow(index),
      cells: [
        DataCell(
          Text(
            caseModel.timestamp.toGermanDateString(),
          ),
        ),
        DataCell(getStatusIcon(caseModel.status)),
        DataCell(Text(caseModel.customerId)),
        DataCell(Text(caseModel.vehicleVin)),
        DataCell(
          Text(caseModels[index].workshopId),
        ),
        DataCell(
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {},
          ),
        )
      ],
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => caseModels.length;

  @override
  int get selectedRowCount => 0;
}
