import "package:aw40_hub_frontend/models/case_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:aw40_hub_frontend/utils/extensions.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";

class CasesDataTableSource extends DataTableSource {
  CasesDataTableSource({
    required this.themeData,
    required this.selectedCaseIndexNotifier,
    required this.caseModels,
    required this.onPressedRow,
  });
  List<CaseModel> caseModels;
  final void Function(int) onPressedRow;
  final ThemeData themeData;
  final ValueNotifier<int?> selectedCaseIndexNotifier;
  final Map<CaseStatus, IconData> caseStatusIcons = {
    CaseStatus.open: Icons.cached,
    CaseStatus.closed: Icons.done,
  };

  Tooltip _getStatusIcon(CaseStatus? caseStatus) {
    return (caseStatus == null)
        ? Tooltip(
            message: tr("general.unnamed"),
            child: const Icon(Icons.question_mark),
          )
        : Tooltip(
            message: tr("cases.status.${caseStatus.name}"),
            child: Icon(caseStatusIcons[caseStatus]),
          );
  }

  @override
  DataRow? getRow(int index) {
    final caseModel = caseModels[index];
    return DataRow(
      onSelectChanged: (_) => onPressedRow(index),
      selected: selectedCaseIndexNotifier.value == index,
      color: MaterialStateProperty.resolveWith<Color?>(
          (Set<MaterialState> states) {
        if (states.contains(MaterialState.selected)) {
          return themeData.colorScheme.primary.withOpacity(0.08);
        }
        return null; // Use the default value.
      }),
      cells: [
        DataCell(
          Text(
            caseModel.timestamp.toGermanDateString(),
          ),
        ),
        DataCell(_getStatusIcon(caseModel.status)),
        DataCell(Text(caseModel.customerId)),
        DataCell(Text(caseModel.vehicleVin)),
        DataCell(
          Text(caseModels[index].workshopId),
        ),
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
