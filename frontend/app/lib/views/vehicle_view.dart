import "package:aw40_hub_frontend/providers/providers.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class VehiclesView extends StatefulWidget {
  const VehiclesView({
    super.key,
  });

  @override
  State<VehiclesView> createState() => _VehiclesViewState();
}

class _VehiclesViewState extends State<VehiclesView> {
  ValueNotifier<int?> currentVehicleIndexNotifier = ValueNotifier<int?>(null);

  @override
  void dispose() {
    currentVehicleIndexNotifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    //return;
  }

}

class VehiclesTable extends StatelessWidget {
    const VehiclesTable({
      required this.vehicle,
      required this. vehicleIndexNotifier,
      super.key,
    });

    final List<VehicleModel> vehicleModel;
    final ValueNotifier<int?> 
  }