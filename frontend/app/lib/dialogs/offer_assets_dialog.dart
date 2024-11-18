import "dart:async";

import "package:aw40_hub_frontend/dtos/new_publication_dto.dart";
import "package:aw40_hub_frontend/dtos/publication_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/forms/offer_assets_form.dart";
import "package:aw40_hub_frontend/providers/assets_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:logging/logging.dart";
import "package:provider/provider.dart";
import "package:routemaster/routemaster.dart";

class OfferAssetsDialog extends StatefulWidget {
  const OfferAssetsDialog({
    super.key,
  });

  @override
  State<OfferAssetsDialog> createState() => _OfferAssetsDialogState();
}

class _OfferAssetsDialogState extends State<OfferAssetsDialog> {
  // ignore: unused_field
  final Logger _logger = Logger("offer_assets_dialog");
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _priceController = TextEditingController();
  final TextEditingController _licenseController = TextEditingController();
  final TextEditingController _privateKeyController = TextEditingController();

  late final AssetProvider _assetProvider;

  final title = tr("assets.upload.title");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: Text(title),
      content: OfferAssetsDialogForm(
        formKey: _formKey,
        priceController: _priceController,
        licenseController: _licenseController,
        privateKeyController: _privateKeyController,
      ),
      actions: [
        TextButton(
          onPressed: () async => _onCancel(context),
          child: Text(
            tr("general.cancel"),
            style: theme.textTheme.labelLarge?.copyWith(
              color: theme.colorScheme.error,
            ),
          ),
        ),
        TextButton(
          onPressed: () async {
            final FormState? currentFormKeyState = _formKey.currentState;
            if (currentFormKeyState != null && currentFormKeyState.validate()) {
              currentFormKeyState.save();

              final double? price = double.tryParse(_priceController.text);
              if (price == null) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "Price was null or invalid.",
                );
              }

              final String licenseType = _licenseController.text;
              if (licenseType.isEmpty) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "License type was not selected.",
                );
              }

              final String privateKeyType = _privateKeyController.text;
              if (privateKeyType.isEmpty) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "PrivateKey type was not null.",
                );
              }

              final bool confirmation =
                  await _showConfirmOfferDialog(context) ?? false;

              if (confirmation) {
                await _uploadAsset(price, licenseType, privateKeyType);
              }
            }
          },
          child: Text(tr("assets.upload.offer")),
        ),
        TextButton(
          onPressed: () async {
            final bool confirmation =
                await _showConfirmRemoveDialog(context) ?? false;

            if (confirmation) {
              // await _removeAsset(context);
            }
          },
          child: Text(
            tr("assets.upload.remove"),
            style: theme.textTheme.labelLarge?.copyWith(
              color: theme.colorScheme.error,
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _uploadAsset(
      double price, String licenseType, String privateKeyType) async {
    _assetProvider = Provider.of<AssetProvider>(context, listen: false);
    final NewPublicationDto newPublicationDto = NewPublicationDto(
      "PONTUSXDEV",
      licenseType,
      price,
      privateKeyType,
    );
    await _assetProvider.publishAsset(newPublicationDto);
  }

  static Future<bool?> _showConfirmOfferDialog(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        //final theme = Theme.of(context);
        return AlertDialog(
          title: Text(tr("assets.confirmation.title")),
          content: Text(tr("assets.confirmation.description")),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(
                tr("general.cancel"),
                //style: theme.textTheme.labelLarge?.copyWith(
                // color: theme.colorScheme.error, ),
              ),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: Text(
                tr("assets.upload.offer"),
              ),
            ),
          ],
        );
      },
    );
  }

  Future<void> _onCancel(BuildContext context) async {
    await Routemaster.of(context).pop();
  }
}

Future<bool?> _showConfirmRemoveDialog(BuildContext context) async {
  final TextEditingController privateKeyController = TextEditingController();

  return showDialog<bool>(
    context: context,
    builder: (BuildContext context) {
      final theme = Theme.of(context);
      return AlertDialog(
        title: Text(tr("assets.remove.title")),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(tr("assets.remove.description")),
            const SizedBox(height: 16),
            TextFormField(
              controller: privateKeyController,
              decoration: InputDecoration(
                labelText: tr("assets.upload.privateKey"),
                border: const OutlineInputBorder(),
              ),
              obscureText: true,
            ),
          ],
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(context, null),
            child: Text(
              tr("general.cancel"),
              style: theme.textTheme.labelLarge?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              final privateKey = privateKeyController.text;
              Navigator.pop(context, privateKey.isNotEmpty ? privateKey : null);
            },
            child: Text(tr("general.confirm")),
          ),
        ],
      );
    },
  );
}

// ignore: must_be_immutable
class OfferAssetsDialogForm extends StatefulWidget {
  const OfferAssetsDialogForm({
    required this.formKey,
    required this.priceController,
    required this.licenseController,
    required this.privateKeyController,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController priceController;
  final TextEditingController licenseController;
  final TextEditingController privateKeyController;

  @override
  State<OfferAssetsDialogForm> createState() => _AddCaseDialogFormState();
}

class _AddCaseDialogFormState extends State<OfferAssetsDialogForm> {
  @override
  Widget build(BuildContext context) {
    return Form(
      key: widget.formKey,
      child: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            OfferAssetsForm(
              priceController: widget.priceController,
              licenseController: widget.licenseController,
              privateKeyController: widget.privateKeyController,
            ),
          ],
        ),
      ),
    );
  }
}
