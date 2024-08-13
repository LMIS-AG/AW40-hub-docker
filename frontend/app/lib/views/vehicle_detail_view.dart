import "package:aw40_hub_frontend/dtos/vehicle_update_dto.dart";
import "package:aw40_hub_frontend/models/vehicle_model.dart";
import "package:aw40_hub_frontend/providers/vehicle_provider.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:logging/logging.dart";
import "package:provider/provider.dart";

class VehicleDetailView extends StatefulWidget {
  const VehicleDetailView({
    required this.vehicleModel,
    required this.onClose,
    super.key,
  });

  final VehicleModel vehicleModel;
  final void Function() onClose;

  @override
  State<VehicleDetailView> createState() => _VehicleDetailView();
}

class _VehicleDetailView extends State<VehicleDetailView> {
  final Logger _logger = Logger("vehicle detail view");
  static const double _spacing = 16;

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    final TextTheme textTheme = Theme.of(context).textTheme;
    final vehicleProvider = Provider.of<VehicleProvider>(context);

    final List<String> attributesCase = [
      tr("general.vin"),
      tr("general.tsn"),
      tr("general.yearBuild"),
    ];
    final List<String> valuesCase = [
      widget.vehicleModel.vin ?? "",
      widget.vehicleModel.tsn ?? "",
      widget.vehicleModel.yearBuild?.toString() ?? "",
    ];

    return SizedBox.expand(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(_spacing),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              IconButton(
                icon: const Icon(Icons.keyboard_double_arrow_right),
                iconSize: 28,
                onPressed: widget.onClose,
                style: IconButton.styleFrom(
                  foregroundColor: colorScheme.primary,
                ),
              ),
              // Title bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    tr("vehicles.details.headline"),
                    style: textTheme.displaySmall,
                  ),
                ],
              ),
              const SizedBox(height: _spacing),
              Table(
                columnWidths: const {0: IntrinsicColumnWidth()},
                children: List.generate(
                  attributesCase.length,
                  (i) => TableRow(
                    children: [
                      const SizedBox(height: 32),
                      Text(attributesCase[i]),
                      Text(valuesCase[i]),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  FilledButton.icon(
                    icon: const Icon(Icons.edit),
                    label: Text(tr("general.edit")),
                    onPressed: () async {
                      final VehicleUpdateDto? vehicleUpdateDto =
                          await _showUpdateCaseDialog(widget.vehicleModel);
                      if (vehicleUpdateDto == null ||
                          widget.vehicleModel.id == null) return;
                      await vehicleProvider.updateVehicle(
                        widget.vehicleModel.id!,
                        vehicleUpdateDto,
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<VehicleUpdateDto?> _showUpdateCaseDialog(
      VehicleModel vehicleModel) async {
    return showDialog<VehicleUpdateDto>(
      context: context,
      builder: (BuildContext context) {
        return const Placeholder();
        // TODO implement
        // return UpdateVehicleDialog(vehicleModel: vehicleModel);
      },
    );
  }
}
