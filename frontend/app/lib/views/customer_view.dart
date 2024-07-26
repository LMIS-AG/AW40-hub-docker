import "package:aw40_hub_frontend/data_sources/customer_data_table_source.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/providers/customer_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class CustomerView extends StatefulWidget {
  const CustomerView({
    super.key,
  });

  @override
  State<CustomerView> createState() => _CustomerViewState();
}

class _CustomerViewState extends State<CustomerView> {
  final currentVehicleIndexNotifier = ValueNotifier<int?>(null);

  @override
  void dispose() {
    currentVehicleIndexNotifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final costumerProvider = Provider.of<CustomerProvider>(context);
    return FutureBuilder(
      // ignore: discarded_futures
      future: costumerProvider.getCustomers(),
      builder:
          (BuildContext context, AsyncSnapshot<List<CustomerModel>> snapshot) {
        if (snapshot.connectionState != ConnectionState.done ||
            !snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final List<CustomerModel>? customerModels = snapshot.data;
        if (customerModels == null) {
          throw AppException(
            exceptionType: ExceptionType.notFound,
            exceptionMessage: "Received no vehicles.",
          );
        }
        return Row(
          children: [
            Expanded(
              flex: 3,
              child: SingleChildScrollView(
                child: PaginatedDataTable(
                  source: CustomerDataTableSource(
                    themeData: Theme.of(context),
                    currentIndexNotifier: currentVehicleIndexNotifier,
                    customerModels: customerModels,
                    onPressedRow: (int i) {
                      currentVehicleIndexNotifier.value = i;
                    },
                  ),
                  showCheckboxColumn: false,
                  rowsPerPage: 50,
                  columns: [
                    DataColumn(label: Text(tr("costumer.headlines.id"))),
                  ],
                ),
              ),
            ),
          ],
        );

        // Show detail view if a case is selected.
        /*ValueListenableBuilder(
              valueListenable: currentVehicleIndexNotifier,
              builder: (context, value, child) {
                if (value == null) return const SizedBox.shrink();
                return Expanded(
                  flex: 2,
                  child: VehiclesDetailView(
                    caseModel: caseModels[value],
                    onClose: () => currentCaseIndexNotifier.value = null,
                  ),
                );
              },
            )*/
      },
    );
  }
}

/*class VehiclesTable extends StatelessWidget {
  const VehiclesTable({
    required this.vehicleModel,
    required this.vehicleIndexNotifier,
    super.key,
  });

  final List<VehicleModel> vehicleModel;
  final ValueNotifier<int?> vehicleIndexNotifier;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: PaginatedDataTable(
        source: VehiclesDataTableSource(
          themeData: Theme.of(context),
          currentIndexNotifier: vehicleIndexNotifier,
          vehicleModels: vehicleModel,
          onPressedRow: (int i) {
            vehicleIndexNotifier.value = i;
          },
        ),
        showCheckboxColumn: false,
        rowsPerPage: 50,
        columns: [
          DataColumn(
            label: Text(tr("general.date")),
            numeric: true,
          ),
          DataColumn(label: Text(tr("general.status"))),
          DataColumn(label: Text(tr("general.customer"))),
          DataColumn(label: Text("${tr('general.vehicle')} VIN")),
          DataColumn(
            label: Text(tr("general.workshop")),
            numeric: true,
          ),
        ],
      ),
    );
  }
}*/
