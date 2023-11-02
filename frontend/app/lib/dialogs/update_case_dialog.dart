import "dart:async";

import "package:aw40_hub_frontend/components/components.dart";
import "package:aw40_hub_frontend/dtos/dtos.dart";
import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/text_input_formatters/text_input_formatters.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "package:logging/logging.dart";
import "package:routemaster/routemaster.dart";

class UpdateCaseDialog extends StatefulWidget {
  const UpdateCaseDialog({
    super.key,
  });

  @override
  State<UpdateCaseDialog> createState() => _UpdateCaseDialogState();
}

class _UpdateCaseDialogState extends State<UpdateCaseDialog> {
  // ignore: unused_field
  final Logger _logger = Logger("update_case_dialog");
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _statusController = TextEditingController();
  final TextEditingController _occasionController = TextEditingController();
  final TextEditingController _timestampController = TextEditingController(
      // TODO maybe get value (as default value) from caseModel - maybe pass it to dialog...
      /*text:
        "${dateTime.day}.${dateTime.month}.${dateTime.year} ${dateTime.hour}:${dateTime.minute}",*/
      );
  final TextEditingController _milageController = TextEditingController();

  void _submitUpdateCaseForm() {
    final FormState? currentFormKeyState = _formKey.currentState;
    if (currentFormKeyState != null && currentFormKeyState.validate()) {
      currentFormKeyState.save();
      final CaseStatus? caseStatus = EnumToString.fromString(
        CaseStatus.values,
        _statusController.text,
      );
      if (caseStatus == null) {
        throw AppException(
          exceptionType: ExceptionType.unexpectedNullValue,
          exceptionMessage: "CaseStatus was null.",
        );
      }
      final CaseOccasion? caseOccasion = EnumToString.fromString(
        CaseOccasion.values,
        _occasionController.text,
      );
      if (caseOccasion == null) {
        throw AppException(
          exceptionType: ExceptionType.unexpectedNullValue,
          exceptionMessage: "CaseOccasion was null.",
        );
      }
      final DateTime? timestamp = DateTime.tryParse(_timestampController.text);
      if (timestamp == null) {
        throw AppException(
          exceptionType: ExceptionType.unexpectedNullValue,
          exceptionMessage: "Timestamp was null.",
        );
      }
      final int? milage = int.tryParse(_milageController.text);
      if (milage == null) {
        throw AppException(
          exceptionType: ExceptionType.unexpectedNullValue,
          exceptionMessage: "Milage was null.",
        );
      }

      final CaseUpdateDto caseUpdateDto = CaseUpdateDto(
        timestamp,
        caseOccasion,
        milage,
        caseStatus,
      );
      unawaited(Routemaster.of(context).pop<CaseUpdateDto>(caseUpdateDto));
    }
  }

  Future<void> _onCancel(BuildContext context) async {
    await Routemaster.of(context).pop();
  }

  final title = tr("cases.actions.updateCase");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return EnvironmentService().isMobilePlatform
        ? FullScreenDialog(
            title: title,
            trailing: TextButton(
              onPressed: _submitUpdateCaseForm,
              child: Text(tr("general.save")),
            ),
            onCancel: () async => _onCancel(context),
            content: UpdateDialogForm(
              formKey: _formKey,
              statusController: _statusController,
              occasionController: _occasionController,
              timestampController: _timestampController,
              milageController: _milageController,
            ),
          )
        : AlertDialog(
            title: Text(title),
            content: UpdateDialogForm(
              formKey: _formKey,
              statusController: _statusController,
              occasionController: _occasionController,
              timestampController: _timestampController,
              milageController: _milageController,
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
                onPressed: _submitUpdateCaseForm,
                child: Text(tr("general.save")),
              ),
            ],
          );
  }
}

// TODO adjust regarding update Case
class UpdateDialogForm extends StatelessWidget {
  const UpdateDialogForm({
    required this.formKey,
    required this.statusController,
    required this.occasionController,
    required this.timestampController,
    required this.milageController,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController statusController;
  final TextEditingController occasionController;
  final TextEditingController timestampController;
  final TextEditingController milageController;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  tr("general.status"),
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
              FormField(
                initialValue: CaseStatus.open, // TODO get value from caseModel
                onSaved: (CaseStatus? newValue) {
                  if (newValue == null) {
                    throw AppException(
                      exceptionType: ExceptionType.unexpectedNullValue,
                      exceptionMessage: "Status was null.",
                    );
                  }
                  occasionController.text =
                      EnumToString.convertToString(newValue);
                },
                builder: (FormFieldState<CaseStatus> field) {
                  return SegmentedButton(
                    emptySelectionAllowed: true,
                    segments: <ButtonSegment<CaseStatus>>[
                      ButtonSegment<CaseStatus>(
                        value: CaseStatus.open,
                        label: Text(tr("cases.status.open")),
                      ),
                      ButtonSegment<CaseStatus>(
                        value: CaseStatus.closed,
                        label: Text(tr("cases.status.closed")),
                      ),
                    ],
                    selected: {field.value},
                    onSelectionChanged: (p0) {
                      // TODO adjust (unknown does not exist for CaseStatus...)
                      final CaseStatus newVal =
                          p0.isEmpty ? CaseStatus.open : p0.first!;
                      // newCaseDto.occasion = newVal;
                      field.didChange(newVal);
                    },
                  );
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  tr("general.occasion"),
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
              FormField(
                initialValue: CaseOccasion.unknown,
                onSaved: (CaseOccasion? newValue) {
                  if (newValue == null) {
                    throw AppException(
                      exceptionType: ExceptionType.unexpectedNullValue,
                      exceptionMessage: "Occasion was null.",
                    );
                  }
                  occasionController.text =
                      EnumToString.convertToString(newValue);
                },
                builder: (FormFieldState<CaseOccasion> field) {
                  return SegmentedButton(
                    emptySelectionAllowed: true,
                    segments: <ButtonSegment<CaseOccasion>>[
                      ButtonSegment<CaseOccasion>(
                        value: CaseOccasion.service_routine,
                        label: Text(tr("cases.occasions.service")),
                      ),
                      ButtonSegment<CaseOccasion>(
                        value: CaseOccasion.problem_defect,
                        label: Text(tr("cases.occasions.problem")),
                      ),
                    ],
                    selected: {field.value},
                    onSelectionChanged: (p0) {
                      final CaseOccasion newVal =
                          p0.isEmpty ? CaseOccasion.unknown : p0.first!;
                      // newCaseDto.occasion = newVal;
                      field.didChange(newVal);
                    },
                  );
                },
              ),
            ],
          ),
          // TODO add timestamp
          /*const SizedBox(height: 16),
          TextFormField(
            decoration: InputDecoration(
              labelText: tr("general.customerId"),
              border: const OutlineInputBorder(),
            ),
            controller: customerIdController,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return tr("general.obligatoryField");
              }
              return null;
            },
            onSaved: (customerId) {
              if (customerId == null) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "CustomerId was null, validation failed.",
                );
              }
              if (customerId.isEmpty) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "CustomerId was empty, validation failed.",
                );
              }
            },
          ),*/
          const SizedBox(height: 16),
          TextFormField(
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            controller: milageController,
            decoration: InputDecoration(
              labelText: tr("general.milage"),
              border: const OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return tr("general.obligatoryField");
              }
              return null;
            },
            onSaved: (customerId) {
              if (customerId == null) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "Milage was null, validation failed.",
                );
              }
              if (customerId.isEmpty) {
                throw AppException(
                  exceptionType: ExceptionType.unexpectedNullValue,
                  exceptionMessage: "Milage was empty, validation failed.",
                );
              }
            },
          ),
        ],
      ),
    );
  }
}
