import "package:aw40_hub_frontend/models/models.dart";
import "package:aw40_hub_frontend/providers/providers.dart";
import "package:aw40_hub_frontend/services/services.dart";
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

  static Future<void> _handleDeleteButtonPress(
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
    super.key,
  });

  final CaseModel caseModel;
  final void Function() onClose;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final LoggedInUserModel loggedInUserModel =
        Provider.of<AuthProvider>(context).loggedInUser;
    return SizedBox.expand(
      child: Card(
        color: theme.colorScheme.primaryContainer,
        child: Column(
          children: [
            // Headbar
            ListTile(
              leading: IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: onClose,
              ),
              title: Text(caseModel.id),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () {},
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () async =>
                        CaseDetailView._handleDeleteButtonPress(
                      context,
                      loggedInUserModel,
                      caseModel.id,
                    ),
                  ),
                ],
              ),
            ),
            // Content
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    "Case Detail View: ${caseModel.id}",
                    style: theme.textTheme.displaySmall,
                  ),
                ],
              ),
            ),
          ],
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
            onPressed: () async => CaseDetailView._handleDeleteButtonPress(
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
