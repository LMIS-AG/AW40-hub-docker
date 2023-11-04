import "dart:async";

import "package:aw40_hub_frontend/components/components.dart";
import "package:aw40_hub_frontend/dtos/dtos.dart";
import "package:aw40_hub_frontend/exceptions/exceptions.dart";
import "package:aw40_hub_frontend/models/case_model.dart";
import "package:aw40_hub_frontend/services/services.dart";
import "package:aw40_hub_frontend/utils/utils.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "package:logging/logging.dart";
import "package:routemaster/routemaster.dart";

class UpdateCaseDialog extends StatefulWidget {
  const UpdateCaseDialog({
    required this.caseModel,
    super.key,
  });

  final CaseModel caseModel;

  @override
  State<UpdateCaseDialog> createState() => _UpdateCaseDialogState();
}

class _UpdateCaseDialogState extends State<UpdateCaseDialog> {
  final Logger _logger = Logger("update_case_dialog");
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _statusController = TextEditingController();
  final TextEditingController _occasionController = TextEditingController();
  final TextEditingController _timestampController = TextEditingController();
  final TextEditingController _milageController = TextEditingController();
  final title = tr("cases.actions.updateCase");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    _milageController.text = widget.caseModel.milage.toString();
    _timestampController.text =
        widget.caseModel.timestamp.toGermanDateTimeString();

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
              caseModel: widget.caseModel,
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
              caseModel: widget.caseModel,
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
      final DateTime? timestamp = _timestampController.text.toDateTime();
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
        caseOccasion ?? CaseOccasion.unknown,
        milage,
        caseStatus,
      );
      unawaited(Routemaster.of(context).pop<CaseUpdateDto>(caseUpdateDto));
    }
  }

  Future<void> _onCancel(BuildContext context) async {
    await Routemaster.of(context).pop();
  }
}

class UpdateDialogForm extends StatelessWidget {
  const UpdateDialogForm({
    required this.formKey,
    required this.statusController,
    required this.occasionController,
    required this.timestampController,
    required this.milageController,
    required this.caseModel,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController statusController;
  final TextEditingController occasionController;
  final TextEditingController timestampController;
  final TextEditingController milageController;
  final CaseModel caseModel;

  @override
  Widget build(BuildContext context) {
    CaseStatus selectedStatus = caseModel.status;
    CaseOccasion selectedOccasion = caseModel.occasion;

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
                onSaved: (CaseStatus? newValue) {
                  if (newValue == null) {
                    throw AppException(
                      exceptionType: ExceptionType.unexpectedNullValue,
                      exceptionMessage: "Status was null.",
                    );
                  }
                  statusController.text =
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
                    selected: {selectedStatus},
                    onSelectionChanged: (p0) {
                      // TODO adjust (unknown does not exist for CaseStatus...)
                      final CaseStatus newVal =
                          p0.isEmpty ? CaseStatus.open : p0.first!;
                      // newCaseDto.status = newVal;
                      selectedStatus = newVal;
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
                onSaved: (CaseOccasion? newValue) {
                  if (newValue != null) {
                    occasionController.text =
                        EnumToString.convertToString(newValue);
                  }
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
                    selected: {selectedOccasion},
                    onSelectionChanged: (p0) {
                      final CaseOccasion newVal =
                          p0.isEmpty ? CaseOccasion.unknown : p0.first!;
                      // newCaseDto.occasion = newVal;
                      selectedOccasion = newVal;
                      field.didChange(newVal);
                    },
                  );
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          TextFormField(
            readOnly: true,
            controller: timestampController,
            decoration: InputDecoration(
              labelText: tr("general.date"),
              border: const OutlineInputBorder(),
            ),
            onTap: () async {
              DateTime? selectedDateTime = await pickDateTime(context);
              if (selectedDateTime != null) {
                timestampController.text =
                    selectedDateTime.toGermanDateTimeString();
              }
            },
          ),
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

  Future<DateTime?> pickDateTime(BuildContext context) async {
    final DateTime? date = await pickDate(context);
    if (date == null) return null;

    final TimeOfDay? time = await pickTime(context);
    if (time == null) return null;

    return DateTime(date.year, date.month, date.day, time.hour, time.minute);
  }

  Future<DateTime?> pickDate(BuildContext context) => showDatePicker(
        context: context,
        initialDate: caseModel.timestamp,
        firstDate: DateTime(1900),
        lastDate: DateTime(2100),
      );

  Future<TimeOfDay?> pickTime(BuildContext context) => showTimePicker(
        context: context,
        initialTime: TimeOfDay.fromDateTime(
          caseModel.timestamp,
        ),
      );
}
