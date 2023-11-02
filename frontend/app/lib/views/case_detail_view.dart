// ignore_for_file: lines_longer_than_80_chars

import "package:aw40_hub_frontend/dtos/case_update_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:aw40_hub_frontend/utils/extensions.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "package:provider/provider.dart";

import "../dialogs/update_case_dialog.dart";

class CaseDetailView extends StatelessWidget {
  const CaseDetailView({
    required this.caseModel,
    required this.onClose,
    super.key,
  });

  final CaseModel caseModel;
  final void Function() onClose;

  @override
  Widget build(BuildContext context) {
    return EnvironmentService().isMobilePlatform
        ? MobileCaseDetailView(
            caseModel: caseModel,
            onDelete: () async => _onDeleteButtonPress(
              context,
              Provider.of<AuthProvider>(context, listen: false).loggedInUser,
              caseModel.id,
            ),
          )
        : DesktopCaseDetailView(
            caseModel: caseModel,
            onClose: onClose,
            onDelete: () async => _onDeleteButtonPress(
              context,
              Provider.of<AuthProvider>(context, listen: false).loggedInUser,
              caseModel.id,
            ),
          );
  }

  static Future<bool?> _showConfirmDeleteDialog(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(tr("cases.details.dialog.title")),
          content: Text(tr("cases.details.dialog.description")),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(tr("general.cancel")),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              style: TextButton.styleFrom(
                foregroundColor: Theme.of(context).colorScheme.error,
              ),
              child: Text(
                tr("general.delete"),
              ),
            ),
          ],
        );
      },
    );
  }

  static Future<void> _onDeleteButtonPress(
    BuildContext context,
    LoggedInUserModel loggedInUserModel,
    String caseModelId,
  ) async {
    final caseProvider = Provider.of<CaseProvider>(
      context,
      listen: false,
    );

    await _showConfirmDeleteDialog(context).then((bool? dialogResult) async {
      final ScaffoldMessengerState scaffoldMessengerState =
          ScaffoldMessenger.of(context);
      if (dialogResult == null || !dialogResult) return;
      final bool result = await caseProvider.deleteCase(caseModelId);
      final String message = result
          ? tr("cases.details.deleteCaseSuccessMessage")
          : tr("cases.details.deleteCaseErrorMessage");
      _showMessage(message, scaffoldMessengerState);
    });
  }

  static void _showMessage(String text, ScaffoldMessengerState state) {
    final SnackBar snackBar = SnackBar(
      content: Center(child: Text(text)),
    );
    state.showSnackBar(snackBar);
  }
}

class DesktopCaseDetailView extends StatefulWidget {
  const DesktopCaseDetailView({
    required this.caseModel,
    required this.onClose,
    required this.onDelete,
    super.key,
  });

  final CaseModel caseModel;
  final void Function() onClose;
  final void Function() onDelete;

  @override
  State<DesktopCaseDetailView> createState() => _DesktopCaseDetailViewState();
}

class _DesktopCaseDetailViewState extends State<DesktopCaseDetailView> {
  // TODO get value from caseModel
  DateTime dateTime = DateTime(
    2023,
    10,
    26,
    14,
    30,
  );

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final caseProvider = Provider.of<CaseProvider>(context, listen: false);

    final List<String> attributes = [
      tr("general.id"),
      tr("general.status"),
      tr("general.occasion"),
      tr("general.date"),
      tr("general.milage"),
      tr("general.customerId"),
      tr("general.vehicleVin"),
      tr("general.workshopId"),
    ];
    final List<String> values = [
      widget.caseModel.id,
      tr("cases.details.status.${widget.caseModel.status.name}"),
      tr("cases.details.occasion.${widget.caseModel.occasion.name}"),
      widget.caseModel.timestamp.toGermanDateString(),
      widget.caseModel.milage.toString(),
      widget.caseModel.customerId,
      widget.caseModel.vehicleVin,
      widget.caseModel.workshopId,
    ];

    return SizedBox.expand(
      child: Card(
        color: theme.colorScheme.primaryContainer,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              AppBar(
                backgroundColor: const Color.fromARGB(0, 0, 0, 0),
                leading: IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: widget.onClose,
                ),
                title: Text(
                  tr("cases.details.headline"),
                  style: Theme.of(context).textTheme.displaySmall,
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () async {
                      final CaseUpdateDto? caseUpdateDto =
                          await _showUpdateCaseDialog(widget.caseModel);
                      if (caseUpdateDto == null) return;
                      await caseProvider.updateCase(
                          widget.caseModel.id, caseUpdateDto);
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: widget.onDelete,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Table(
                columnWidths: const {0: IntrinsicColumnWidth()},
                children: List.generate(
                  attributes.length,
                  (i) => TableRow(
                    children: [
                      const SizedBox(height: 32),
                      Text(attributes[i]),
                      Text(values[i]),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<CaseUpdateDto?> _showUpdateCaseDialog(CaseModel caseModel) async {
    final CaseUpdateDto? updatedCase = await showDialog<CaseUpdateDto>(
      context: context,
      builder: (BuildContext context) {
        return UpdateCaseDialog(caseModel: caseModel);
      },
    );
    return updatedCase;
  }

// TODO remove
  /* Future pickDateTime() async {
    final DateTime? date = await pickDate();
    if (date == null) return;

    final TimeOfDay? time = await pickTime();
    if (time == null) return;

    final selectedDateTime =
        DateTime(date.year, date.month, date.day, time.hour, time.minute);

    setState(() => dateTime = selectedDateTime);
  }

  Future<DateTime?> pickDate() => showDatePicker(
        context: context,
        initialDate: dateTime,
        firstDate: DateTime(1900),
        lastDate: DateTime(2100),
      );

  Future<TimeOfDay?> pickTime() => showTimePicker(
        context: context,
        initialTime: TimeOfDay.fromDateTime(dateTime),
      ); */
}

class MobileCaseDetailView extends StatelessWidget {
  const MobileCaseDetailView({
    required this.caseModel,
    required this.onDelete,
    super.key,
  });

  final CaseModel caseModel;
  final void Function() onDelete;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);

    return ListTile(
      tileColor: theme.colorScheme.primaryContainer,
      title: const Text("Case Detail View"),
      subtitle: Text("ID: ${caseModel.id}"),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: onDelete,
          ),
        ],
      ),
    );
  }
}
