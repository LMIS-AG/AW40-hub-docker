// ignore_for_file: lines_longer_than_80_chars

import "package:aw40_hub_frontend/models/diagnosis_model.dart";
import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/utils/extensions.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class DiagnosisDetailView extends StatelessWidget {
  const DiagnosisDetailView({
    required this.diagnosisModel,
    required this.onClose,
    super.key,
  });

  final DiagnosisModel diagnosisModel;
  final void Function() onClose;

  @override
  Widget build(BuildContext context) {
    return DesktopDiagnosisDetailView(
      diagnosisModel: diagnosisModel,
      onClose: onClose,
      onDelete: () async => _onDeleteButtonPress(
        context,
        Provider.of<AuthProvider>(context, listen: false).loggedInUser,
        diagnosisModel.id,
      ),
    );
  }

  static Future<void> _onDeleteButtonPress(
    BuildContext context,
    LoggedInUserModel loggedInUserModel,
    String diagnosisModelId,
  ) async {
    final diagnosisProvider = Provider.of<DiagnosisProvider>(
      context,
      listen: false,
    );

    await _showConfirmDeleteDialog(context).then((bool? dialogResult) async {
      final ScaffoldMessengerState scaffoldMessengerState =
          ScaffoldMessenger.of(context);
      if (dialogResult == null || !dialogResult) return;
      final bool result =
          await diagnosisProvider.deleteDiagnosis(diagnosisModelId);
      final String message = result
          ? tr("diagnosis.details.deleteCaseSuccessMessage")
          : tr("diagnosis.details.deleteCaseErrorMessage");
      _showMessage(message, scaffoldMessengerState);
    });
  }

  static Future<bool?> _showConfirmDeleteDialog(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(tr("diagnosis.details.dialog.title")),
          content: Text(tr("diagnosis.details.dialog.description")),
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

  static void _showMessage(String text, ScaffoldMessengerState state) {
    final SnackBar snackBar = SnackBar(
      content: Center(child: Text(text)),
    );
    state.showSnackBar(snackBar);
  }
}

class DesktopDiagnosisDetailView extends StatefulWidget {
  const DesktopDiagnosisDetailView({
    required this.diagnosisModel,
    required this.onClose,
    required this.onDelete,
    super.key,
  });

  final DiagnosisModel diagnosisModel;
  final void Function() onClose;
  final void Function() onDelete;

  @override
  State<DesktopDiagnosisDetailView> createState() =>
      _DesktopDiagnosisDetailView();
}

class _DesktopDiagnosisDetailView extends State<DesktopDiagnosisDetailView> {
  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);

    // TODO adjust this section in Story 61883
    final List<String> attributes = [
      tr("general.id"),
      tr("general.status"),
      tr("general.date"),
      tr("general.case"),
    ];
    final List<String> values = [
      widget.diagnosisModel.id,
      tr("diagnosis.status.${widget.diagnosisModel.status.name}"),
      widget.diagnosisModel.timestamp.toGermanDateString(),
      widget.diagnosisModel.caseId,
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
                  icon: const Icon(Icons.keyboard_double_arrow_right),
                  iconSize: 28,
                  onPressed: widget.onClose,
                ),
                title: Text(
                  tr("diagnosis.details.headline"),
                  style: Theme.of(context).textTheme.displaySmall,
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.delete_forever),
                    iconSize: 28,
                    color: Theme.of(context).colorScheme.error,
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
}
