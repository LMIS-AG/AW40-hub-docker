import "package:aw40_hub_frontend/forms/base_upload_form.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class UploadTimeseriesForm extends StatefulWidget {
  const UploadTimeseriesForm({super.key});

  @override
  State<UploadTimeseriesForm> createState() => _UploadTimeseriesFormState();
}

class _UploadTimeseriesFormState extends State<UploadTimeseriesForm> {
  final TextEditingController _componentController = TextEditingController();
  final TextEditingController _labelController = TextEditingController();
  final TextEditingController _samplingRateController = TextEditingController();
  final TextEditingController _durationController = TextEditingController();
  final TextEditingController _signalController = TextEditingController();
  TimeseriesDataLabel? selectedLabel;
  final _formKey = GlobalKey<FormState>();
  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: BaseUploadForm(
        content: Column(
          children: [
            TextFormField(
              validator: _textValidation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _componentController,
              decoration: const InputDecoration(
                labelText: "Components",
                hintText: "Enter a Component.",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            DropdownMenu<TimeseriesDataLabel>(
              controller: _labelController,
              label: const Text("Label"),
              onSelected: (TimeseriesDataLabel? timeseriesDataLabel) {
                setState(() {
                  selectedLabel = timeseriesDataLabel;
                });
              },
              dropdownMenuEntries: TimeseriesDataLabel.values
                  .map<DropdownMenuEntry<TimeseriesDataLabel>>(
                (TimeseriesDataLabel timeseriesDataLabel) {
                  return DropdownMenuEntry<TimeseriesDataLabel>(
                    value: timeseriesDataLabel,
                    label: timeseriesDataLabel.name,
                  );
                },
              ).toList(),
            ),
            const SizedBox(height: 16),
            TextFormField(
              validator: _numberValidation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _durationController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Duration",
                hintText: "Enter a Duration.",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              validator: _numberValidation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _samplingRateController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Sampling Rate",
                hintText: "Enter a Sampling Rate.",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              validator: _signalValidation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _signalController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Signal",
                hintText: "Enter signals separated by commas, e.g., 1,2,3",
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        onSubmit: _onSubmit,
      ),
    );
  }

  String? _textValidation(String? value) {
    if (value == null || value.isEmpty) {
      return "Please enter some text";
    }
    return null;
  }

  String? _numberValidation(String? value) {
    if (value == null || value.isEmpty) return "Please enter some signal";
    final int? numberValue = int.tryParse(value);
    if (numberValue == null) {
      return "Please enter a valid number";
    }
    return null;
  }

  String? _signalValidation(String? value) {
    if (value == null || value.isEmpty) {
      return "Please enter a signal";
    }
    final List<String> parts = value.split(",");
    for (final String part in parts) {
      if (part.trim().isEmpty || int.tryParse(part.trim()) == null) {
        return "Each value must be a valid integer separated by commas";
      }
    }
    return null;
  }

  Future<void> _onSubmit() async {
    final FormState? formState = _formKey.currentState;
    if (formState != null && !formState.validate()) return;

    final messengerState = ScaffoldMessenger.of(context);
    final provider = Provider.of<DiagnosisProvider>(context, listen: false);

    final String component = _componentController.text;
    final TimeseriesDataLabel? label = EnumToString.fromString(
      TimeseriesDataLabel.values,
      _labelController.text,
    );
    if (label == null) return;
    final int? samplingRate = int.tryParse(_samplingRateController.text);
    final int? duration = int.tryParse(_durationController.text);
    final List<int> signal = _signalController.text
        .split(",")
        .map((part) => int.parse(part.trim()))
        .toList();

    if (samplingRate == null || duration == null || signal.contains(null)) {
      messengerState.showSnackBar(
        SnackBar(content: Text(tr("Invalid numbers in fields."))),
      );
      return;
    }

    final bool result = await provider.addTimeseriesData(
      provider.workshopId,
      provider.diagnosisCaseId,
      component,
      label,
      samplingRate,
      duration,
      signal,
    );
    final String snackBarText = result
        ? tr("diagnoses.details.uploadDataSuccessMessage")
        : tr("diagnoses.details.uploadDataErrorMessage");
    messengerState.showSnackBar(SnackBar(content: Text(snackBarText)));
  }
}
