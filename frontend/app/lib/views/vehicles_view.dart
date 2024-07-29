import "package:aw40_hub_frontend/data_sources/vehicles_data_table_source.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/vehicle_model.dart";
import "package:aw40_hub_frontend/providers/vehicle_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:logging/logging.dart";
import "package:provider/provider.dart";

class VehiclesView extends StatefulWidget {
  const VehiclesView({
    super.key,
  });

  @override
  State<VehiclesView> createState() => _VehiclesViewState();
}

class _VehiclesViewState extends State<VehiclesView> {
  final currentVehicleIndexNotifier = ValueNotifier<int?>(null);
  Logger vehicleViewLogger = Logger("VehicleViewLogger");

  @override
  void dispose() {
    currentVehicleIndexNotifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vehicleProvider = Provider.of<VehicleProvider>(context);
    return FutureBuilder(
      // ignore: discarded_futures
      future: vehicleProvider.getSharedVehicles(),
      builder:
          (BuildContext context, AsyncSnapshot<List<VehicleModel>> snapshot) {
        if (snapshot.connectionState != ConnectionState.done ||
            !snapshot.hasData) {
          vehicleViewLogger.shout(snapshot.error);
          vehicleViewLogger.shout(snapshot.data);
          return const Center(child: CircularProgressIndicator());
        }
        final List<VehicleModel>? vehicleModels = snapshot.data;
        if (vehicleModels == null) {
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
                  source: VehiclesDataTableSource(
                    themeData: Theme.of(context),
                    currentIndexNotifier: currentVehicleIndexNotifier,
                    vehicleModels: vehicleModels,
                    onPressedRow: (int i) {
                      currentVehicleIndexNotifier.value = i;
                    },
                  ),
                  showCheckboxColumn: false,
                  rowsPerPage: 50,
                  columns: [
                    DataColumn(label: Text(tr("vehicles.headlines.vin"))),
                    DataColumn(label: Text(tr("vehicles.headlines.tsn"))),
                    DataColumn(label: Text(tr("vehicles.headlines.yearBuild"))),
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

class VehiclesTable extends StatelessWidget {
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
}
