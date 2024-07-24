import "package:aw40_hub_frontend/components/file_upload_form_component.dart";
import "package:aw40_hub_frontend/forms/base_upload_form.dart";
import "package:aw40_hub_frontend/providers/diagnosis_provider.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/foundation.dart";
import "package:flutter/material.dart";
import "package:provider/provider.dart";

class UploadPicoscopeForm extends StatefulWidget {
  const UploadPicoscopeForm({super.key});

  @override
  State<UploadPicoscopeForm> createState() => _UploadPicoscopeFormState();
}

class _UploadPicoscopeFormState extends State<UploadPicoscopeForm> {
  Uint8List? _file;
  String? _filename;
  final TextEditingController _componentAController = TextEditingController();
  final TextEditingController _componentBController = TextEditingController();
  final TextEditingController _componentCController = TextEditingController();
  final TextEditingController _labelAController = TextEditingController();
  final TextEditingController _labelBController = TextEditingController();
  final TextEditingController _labelCController = TextEditingController();
  PicoscopeLabel? selectedLabelA;
  PicoscopeLabel? selectedLabelB;
  PicoscopeLabel? selectedLabelC;
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: BaseUploadForm(
        content: Column(
          children: [
            FileUploadFormComponent(
              onFileDrop: (Uint8List file, String name) {
                _file = file;
                _filename = name;
              },
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    controller: _componentAController,
                    decoration: const InputDecoration(
                      labelText: "Component A",
                      hintText: "Enter a Component",
                      border: OutlineInputBorder(),
                      suffixText: "optional",
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownMenu<PicoscopeLabel>(
                    controller: _labelAController,
                    label: const Text("Label"),
                    hintText: "optional",
                    onSelected: (PicoscopeLabel? picoscopeLabel) {
                      setState(() {
                        selectedLabelA = picoscopeLabel;
                      });
                    },
                    dropdownMenuEntries: PicoscopeLabel.values
                        .map<DropdownMenuEntry<PicoscopeLabel>>(
                      (PicoscopeLabel picoscopeLabel) {
                        return DropdownMenuEntry<PicoscopeLabel>(
                          value: picoscopeLabel,
                          label: picoscopeLabel.name,
                        );
                      },
                    ).toList(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    controller: _componentBController,
                    decoration: const InputDecoration(
                      labelText: "Component B",
                      hintText: "Enter a Component",
                      border: OutlineInputBorder(),
                      suffixText: "optional",
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownMenu<PicoscopeLabel>(
                    controller: _labelBController,
                    label: const Text("Label"),
                    hintText: "optional",
                    onSelected: (PicoscopeLabel? picoscopeLabel) {
                      setState(() {
                        selectedLabelB = picoscopeLabel;
                      });
                    },
                    dropdownMenuEntries: PicoscopeLabel.values
                        .map<DropdownMenuEntry<PicoscopeLabel>>(
                      (PicoscopeLabel timeseriesDataLabel) {
                        return DropdownMenuEntry<PicoscopeLabel>(
                          value: timeseriesDataLabel,
                          label: timeseriesDataLabel.name,
                        );
                      },
                    ).toList(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    controller: _componentCController,
                    decoration: const InputDecoration(
                      labelText: "Component C",
                      hintText: "Enter a Component",
                      border: OutlineInputBorder(),
                      suffixText: "optional",
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownMenu<PicoscopeLabel>(
                    controller: _labelCController,
                    label: const Text("Label"),
                    hintText: "optional",
                    onSelected: (PicoscopeLabel? picoscopeLabel) {
                      setState(() {
                        selectedLabelC = picoscopeLabel;
                      });
                    },
                    dropdownMenuEntries: PicoscopeLabel.values
                        .map<DropdownMenuEntry<PicoscopeLabel>>(
                      (PicoscopeLabel timeseriesDataLabel) {
                        return DropdownMenuEntry<PicoscopeLabel>(
                          value: timeseriesDataLabel,
                          label: timeseriesDataLabel.name,
                        );
                      },
                    ).toList(),
                  ),
                ),
              ],
            ),
          ],
        ),
        onSubmit: _onSubmit,
      ),
    );
  }

  Future<void> _onSubmit() async {
    final messengerState = ScaffoldMessenger.of(context);
    final Uint8List? file = _file;
    if (file == null) {
      messengerState.showSnackBar(
        SnackBar(
          content: Text(tr("diagnoses.details.uploadDataErrorMessage")),
        ),
      );
      return;
    }
    final FormState? formState = _formKey.currentState;
    if (formState != null && !formState.validate()) return;

    final provider = Provider.of<DiagnosisProvider>(context, listen: false);
    final String? filename = _filename;
    if (filename == null) return;

    final String componentA = _componentAController.text;
    final String componentB = _componentBController.text;
    final String componentC = _componentCController.text;
    //if (_labelAController.text.isEmpty) return;
    final PicoscopeLabel? labelA =
        EnumToString.fromString(PicoscopeLabel.values, _labelAController.text);
    final PicoscopeLabel? labelB =
        EnumToString.fromString(PicoscopeLabel.values, _labelBController.text);
    final PicoscopeLabel? labelC =
        EnumToString.fromString(PicoscopeLabel.values, _labelCController.text);

    final bool result = await provider.uploadPicoscopeData(
      provider.diagnosisCaseId,
      file,
      filename,
      componentA,
      componentB,
      componentC,
      labelA,
      labelB,
      labelC,
    );

    final String snackBarText = result
        ? tr("diagnoses.details.uploadDataSuccessMessage")
        : tr("diagnoses.details.uploadDataErrorMessage");
    messengerState.showSnackBar(SnackBar(content: Text(snackBarText)));
  }
}
