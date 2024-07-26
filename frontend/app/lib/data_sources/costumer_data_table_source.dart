import "package:aw40_hub_frontend/models/costumer_model.dart";
import "package:flutter/material.dart";

class CostumersDataTableSource extends DataTableSource {
  CostumersDataTableSource({
    required this.themeData,
    required this.currentIndexNotifier,
    required this.costumerModels,
    required this.onPressedRow,
  });
  List<CostumerModel> costumerModels;
  final void Function(int) onPressedRow;
  final ThemeData themeData;
  final ValueNotifier<int?> currentIndexNotifier;

  @override
  DataRow? getRow(int index) {
    final costumerModel = costumerModels[index];
    return DataRow(
      onSelectChanged: (_) => onPressedRow(index),
      selected: currentIndexNotifier.value == index,
      color: MaterialStateProperty.resolveWith<Color?>(
          (Set<MaterialState> states) {
        if (states.contains(MaterialState.selected)) {
          return themeData.colorScheme.primary.withOpacity(0.08);
        }
        return null; // Use the default value.
      }),
      cells: [
        DataCell(
          Text(costumerModel.id.name),
        ),
      ],
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => costumerModels.length;

  @override
  int get selectedRowCount => 0;
}
