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
  final TextEditingController _labelAController = TextEditingController();
  PicoscopeLabel? selectedLabelA;
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
              //mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Expanded(
                  flex: 3,
                  child: TextFormField(
                    //validator: _validation,
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    controller: _componentAController,
                    decoration: const InputDecoration(
                      labelText: "Component A",
                      hintText: "Enter a Component",
                      border: OutlineInputBorder(),
                      suffixText: "optional",
                      //suffixStyle: TextStyle(fontSize: 14, color: Colors.grey),
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
            /*TextFormField(
              //validator: _validation,
              autovalidateMode: AutovalidateMode.onUserInteraction,
              controller: _componentAController,
              decoration: const InputDecoration(
                labelText: "Component A",
                hintText: "Enter a Component",
                border: OutlineInputBorder(),
                suffixText: "optional",
              ),
            ),
            const SizedBox(height: 16),
            DropdownMenu<PicoscopeLabel>(
              controller: _labelAController,
              label: const Text("Label"),
              onSelected: (PicoscopeLabel? picoscopeLabel) {
                setState(() {
                  selectedLabelA = picoscopeLabel;
                });
              },
              dropdownMenuEntries:
                  PicoscopeLabel.values.map<DropdownMenuEntry<PicoscopeLabel>>(
                (PicoscopeLabel timeseriesDataLabel) {
                  return DropdownMenuEntry<PicoscopeLabel>(
                    value: timeseriesDataLabel,
                    label: timeseriesDataLabel.name,
                  );
                },
              ).toList(),
            ),*/
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
    //if (_labelAController.text.isEmpty) return;
    final PicoscopeLabel? labelA =
        EnumToString.fromString(PicoscopeLabel.values, _labelAController.text);

    final bool result = await provider.uploadPicoscopeData(
      provider.diagnosisCaseId,
      file,
      filename,
      componentA,
      labelA,
    );

    final String snackBarText = result
        ? tr("diagnoses.details.uploadDataSuccessMessage")
        : tr("diagnoses.details.uploadDataErrorMessage");
    messengerState.showSnackBar(SnackBar(content: Text(snackBarText)));
  }
}
