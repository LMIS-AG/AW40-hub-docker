import "package:aw40_hub_frontend/forms/base_upload_form.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class UploadSymptomForm extends StatefulWidget {
  const UploadSymptomForm({super.key});

  @override
  State<UploadSymptomForm> createState() => _UploadSymptomFormState();
}

class _UploadSymptomFormState extends State<UploadSymptomForm> {
  final TextEditingController _componentController = TextEditingController();
  final TextEditingController _labelController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: BaseUploadForm(
        content: Column(
          children: [
            TextFormField(
              validator: _validation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _componentController,
              minLines: 1,
              maxLines: null,
              decoration: const InputDecoration(
                labelText: "Components",
                hintText: "Enter a Component.",
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        onSubmit: _onSubmit,
      ),
    );
  }

  String? _validation(String? value) {
    if (value == null || value.isEmpty) {
      return "Please enter some text";
    }

    return null;
  }

  Future<void> _onSubmit() async {
    final messengerState = ScaffoldMessenger.of(context);
    final FormState? formState = _formKey.currentState;
    if (formState != null && !formState.validate()) return;

    final provider = Provider.of<DiagnosisProvider>(context, listen: false);

    final String component = _componentController.text;
    final SymptomLabel? label =
        EnumToString.fromString(SymptomLabel.values, _labelController.text);

    final bool result = await provider.uploadSymptomData(
      provider.diagnosisCaseId,
      component,
      label,
    );
    final String snackBarText = result
        ? tr("diagnoses.details.uploadDataSuccessMessage")
        : tr("diagnoses.details.uploadDataErrorMessage");
    messengerState.showSnackBar(SnackBar(content: Text(snackBarText)));
  }
}
