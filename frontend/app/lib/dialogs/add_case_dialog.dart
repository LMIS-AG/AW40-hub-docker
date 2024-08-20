import "dart:async";

import "package:aw40_hub_frontend/dtos/new_case_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/providers/customer_provider.dart";
import "package:aw40_hub_frontend/text_input_formatters/upper_case_text_input_formatter.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:enum_to_string/enum_to_string.dart";
import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "package:logging/logging.dart";
import "package:provider/provider.dart";
import "package:routemaster/routemaster.dart";

class AddCaseDialog extends StatefulWidget {
  const AddCaseDialog({
    super.key,
  });

  @override
  State<AddCaseDialog> createState() => _AddCaseDialogState();
}

class _AddCaseDialogState extends State<AddCaseDialog> {
  // ignore: unused_field
  final Logger _logger = Logger("add_case_dialog");
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _vinController = TextEditingController();
  final TextEditingController _customerIdController = TextEditingController();
  final TextEditingController _occasionController = TextEditingController();
  final TextEditingController _milageController = TextEditingController();

  void _submitAddCaseForm() {
    final FormState? currentFormKeyState = _formKey.currentState;
    if (currentFormKeyState != null && currentFormKeyState.validate()) {
      currentFormKeyState.save();
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
      final int? milage = int.tryParse(_milageController.text);
      if (milage == null) {
        throw AppException(
          exceptionType: ExceptionType.unexpectedNullValue,
          exceptionMessage: "Milage was null.",
        );
      }
      final NewCaseDto newCaseDto = NewCaseDto(
        _vinController.text,
        _customerIdController.text,
        caseOccasion,
        milage,
      );
      unawaited(Routemaster.of(context).pop<NewCaseDto>(newCaseDto));
    }
  }

  Future<void> _onCancel(BuildContext context) async {
    await Routemaster.of(context).pop();
  }

  final title = tr("cases.actions.addCase");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: Text(title),
      content: AddDialogForm(
        formKey: _formKey,
        vinController: _vinController,
        customerIdController: _customerIdController,
        occasionController: _occasionController,
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
          onPressed: _submitAddCaseForm,
          child: Text(tr("general.save")),
        ),
      ],
    );
  }
}

class AddDialogForm extends StatelessWidget {
  AddDialogForm({
    required this.formKey,
    required this.vinController,
    required this.customerIdController,
    required this.occasionController,
    required this.milageController,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController vinController;
  final TextEditingController customerIdController;
  final TextEditingController occasionController;
  final TextEditingController milageController;

  final customerEntriesMock = [
    "Altmann",
    "Beermann",
    "Czichow",
    "Dubski",
    "Ehrenfeld",
    "Friede",
    "Friedman",
    "Grave",
    "Gravemeier",
    "Grau",
    "Hermann",
    "Hayek",
  ];

  String? lastSelectedCustomer;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      // ignore: discarded_futures
      future: Provider.of<CustomerProvider>(context).getSharedCustomers(),
      builder:
          (BuildContext context, AsyncSnapshot<List<CustomerModel>> snapshot) {
        if (snapshot.connectionState != ConnectionState.done ||
            !snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final List<CustomerModel>? customerModels = snapshot.data;
        if (customerModels == null) {
          throw AppException(
            exceptionType: ExceptionType.notFound,
            exceptionMessage: "Received no customers.",
          );
        }
        return Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                inputFormatters: [UpperCaseTextInputFormatter()],
                decoration: InputDecoration(
                  labelText: tr("general.vehicleVin"),
                  border: const OutlineInputBorder(),
                ),
                controller: vinController,
                onSaved: (vin) {
                  if (vin == null) {
                    throw AppException(
                      exceptionType: ExceptionType.unexpectedNullValue,
                      exceptionMessage: "VIN was null, validation failed.",
                    );
                  }
                  if (vin.isEmpty) {
                    throw AppException(
                      exceptionType: ExceptionType.unexpectedNullValue,
                      exceptionMessage: "VIN was empty, validation failed.",
                    );
                  }
                },
                validator: (String? value) {
                  if (value == null || value.isEmpty) {
                    return tr("general.obligatoryField");
                  }
                  if (value.contains(RegExp("[IOQ]"))) {
                    return tr("cases.addCaseDialog.vinCharactersInvalid");
                  }
                  if (value.length != 17) {
                    return tr("cases.addCaseDialog.vinLengthInvalid");
                  }
                  return null;
                },
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
                      return SizedBox(
                        width: 275,
                        child: SegmentedButton(
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
                        ),
                      );
                    },
                  ),
                ],
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
              const SizedBox(height: 16),
              Row(
                children: [
                  Tooltip(
                    message: tr("cases.addCaseDialog.customerTooltip"),
                    child: DropdownMenu<String>(
                      controller: customerIdController,
                      label: Text(tr("general.customer")),
                      hintText: tr("forms.optional"),
                      enableFilter: true,
                      width: 273,
                      menuHeight: 350,
                      onSelected: (value) async =>
                          _onCustomerSelection(context, value),
                      menuStyle:
                          const MenuStyle(alignment: Alignment.bottomLeft),
                      dropdownMenuEntries: // TODO replace mock data with adjusted customerModels
                          customerEntriesMock.map<DropdownMenuEntry<String>>(
                        (String entry) {
                          return DropdownMenuEntry<String>(
                            value: entry,
                            label: entry,
                          );
                        },
                      ).toList(),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Tooltip(
                    message: tr(
                        "cases.addCaseDialog.customerTooltip"), // TODO adjust
                    child: IconButton(
                      icon: const Icon(Icons.person_add),
                      onPressed: () {
                        // TODO implement
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _onCustomerSelection(
    BuildContext context,
    String? value,
  ) async {
    if (value == null) return;
    await _showConfirmSelectCustomerDialog(context, value)
        .then((bool? dialogResult) async {
      if (dialogResult ?? false) {
        lastSelectedCustomer = customerIdController.text;
      } else {
        if (lastSelectedCustomer == null) {
          customerIdController.clear();
        } else {
          customerIdController.text = lastSelectedCustomer!;
        }
      }
    });
  }

  static Future<bool?> _showConfirmSelectCustomerDialog(
    BuildContext context,
    String value,
  ) {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(tr("cases.addCaseDialog.confirmDialog.title")),
          content: Text(tr(
            "cases.addCaseDialog.confirmDialog.description",
            namedArgs: {"customer": value},
          )),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(tr("general.no")),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              style: TextButton.styleFrom(
                foregroundColor: Theme.of(context).colorScheme.error,
              ),
              child: Text(
                tr("general.yes"),
              ),
            ),
          ],
        );
      },
    );
  }
}
