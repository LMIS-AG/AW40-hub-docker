import "package:aw40_hub_frontend/dtos/new_obd_data_dto.dart";
import "package:aw40_hub_frontend/forms/base_upload_form.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:logging/logging.dart";
import "package:provider/provider.dart";

class UploadObdForm extends StatefulWidget {
  const UploadObdForm({super.key});

  @override
  State<UploadObdForm> createState() => _UploadObdFormState();
}

class _UploadObdFormState extends State<UploadObdForm> {
  // ignore: unused_field
  final Logger _logger = Logger("UploadObdForm");
  final TextEditingController _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BaseUploadForm(
      content: TextFormField(
        validator: _signalValidation,
        autovalidateMode: AutovalidateMode.onUserInteraction,
        controller: _controller,
        decoration: InputDecoration(
          labelText: tr("forms.obd.label"),
          hintText: tr("forms.obd.hint"),
          suffixText: tr("forms.obd.suffix"),
          border: const OutlineInputBorder(),
        ),
      ),
      onSubmit: _onSubmit,
    );
  }

  String? _signalValidation(String? value) {
    if (value == null || value.isEmpty) {
      return tr("forms.validation.enterSignal");
    }
    final List<String> parts = value.split(",");
    for (final String part in parts) {
      if (part.trim().isEmpty) {
        return tr("forms.validation.separateWithComma");
      }
    }
    return null;
  }

  Future<void> _onSubmit() async {
    final provider = Provider.of<DiagnosisProvider>(context, listen: false);
    final messengerState = ScaffoldMessenger.of(context);
    final List<String> codes = _controller.text.split("\n");
    final dto = NewOBDDataDto(null, codes);
    final bool result =
        await provider.uploadObdData(provider.diagnosisCaseId, dto);
    final String snackBarText = result
        ? tr("diagnoses.details.uploadDataSuccessMessage")
        : tr("diagnoses.details.uploadDataErrorMessage");
    messengerState.showSnackBar(SnackBar(content: Text(snackBarText)));
  }
}
