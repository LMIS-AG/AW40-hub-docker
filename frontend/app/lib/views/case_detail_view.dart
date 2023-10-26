import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/extensions.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

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

class DesktopCaseDetailView extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);

    final List<String> attributes = [
      tr("general.id"),
      tr("general.status"),
      tr("general.date"),
      tr("general.occasion"),
      tr("general.milage"),
      tr("general.customerId"),
      tr("general.vehicleVin"),
      tr("general.workshopId"),
    ];
    final List<String> values = [
      caseModel.id,
      tr("cases.details.status.${caseModel.status.name}"),
      caseModel.timestamp.toGermanDateString(),
      tr("cases.details.occasion.${caseModel.occasion.name}"),
      caseModel.milage.toString(),
      caseModel.customerId,
      caseModel.vehicleVin,
      caseModel.workshopId,
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
                  onPressed: onClose,
                ),
                title: Text(
                  tr("cases.details.headline"),
                  style: Theme.of(context).textTheme.displaySmall,
                ),
                actions: [
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

class MobileCaseDetailView extends StatelessWidget {
  const MobileCaseDetailView({
    required this.caseModel,
    super.key,
  });

  final CaseModel caseModel;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final LoggedInUserModel loggedInUserModel =
        Provider.of<AuthProvider>(context).loggedInUser;
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
            onPressed: () async => CaseDetailView._onDeleteButtonPress(
              context,
              loggedInUserModel,
              caseModel.id,
            ),
          ),
        ],
      ),
    );
  }
}
