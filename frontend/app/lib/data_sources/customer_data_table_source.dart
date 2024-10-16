import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/services/helper_service.dart";
import "package:flutter/material.dart";

class CustomerDataTableSource extends DataTableSource {
  CustomerDataTableSource({
    required this.themeData,
    required this.currentIndexNotifier,
    required this.customerModels,
    required this.onPressedRow,
  });
  List<CustomerModel> customerModels;
  final void Function(int) onPressedRow;
  final ThemeData themeData;
  final ValueNotifier<int?> currentIndexNotifier;

  @override
  DataRow? getRow(int index) {
    final customerModel = customerModels[index];
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
        DataCell(Text(customerModel.id ?? "")),
        DataCell(
          Text(
            HelperService.convertIso88591ToUtf8(customerModel.firstname),
          ),
        ),
        DataCell(
          Text(
            HelperService.convertIso88591ToUtf8(customerModel.lastname),
          ),
        ),
        DataCell(
          Text(
            HelperService.convertIso88591ToUtf8(
              customerModel.email ?? "",
            ),
          ),
        ),
        DataCell(Text(customerModel.phone ?? "")),
        DataCell(
          Text(
            HelperService.convertIso88591ToUtf8(
              customerModel.street ?? "",
            ),
          ),
        ),
        DataCell(Text(customerModel.housenumber ?? "")),
        DataCell(Text(customerModel.postcode ?? "")),
        DataCell(
          Text(
            HelperService.convertIso88591ToUtf8(
              customerModel.city ?? "",
            ),
          ),
        ),
      ],
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => customerModels.length;

  @override
  int get selectedRowCount => 0;
}
