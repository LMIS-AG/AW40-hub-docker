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

  final TextEditingController _firstNameController = TextEditingController();
  final TextEditingController _lastNameController = TextEditingController();

  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _zipcodeController = TextEditingController();
  final TextEditingController _cityController = TextEditingController();
  final TextEditingController _streetController = TextEditingController();
  final TextEditingController _housenumberController = TextEditingController();

  final title = tr("cases.actions.addCase");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: Text(title),
      content: AddCaseDialogForm(
        formKey: _formKey,
        vinController: _vinController,
        customerIdController: _customerIdController,
        occasionController: _occasionController,
        milageController: _milageController,
        cityController: _cityController,
        firstNameController: _firstNameController,
        housenumberController: _housenumberController,
        lastNameController: _lastNameController,
        streetController: _streetController,
        zipcodeController: _zipcodeController,
        emailController: _emailController,
        phoneController: _phoneController,
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

  void _submitAddCaseForm() {
    // TODO check whether new customer should be created and read values

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
}

// ignore: must_be_immutable
class AddCaseDialogForm extends StatefulWidget {
  const AddCaseDialogForm({
    required this.formKey,
    required this.vinController,
    required this.customerIdController,
    required this.occasionController,
    required this.milageController,
    required this.firstNameController,
    required this.lastNameController,
    required this.zipcodeController,
    required this.cityController,
    required this.streetController,
    required this.housenumberController,
    required this.phoneController,
    required this.emailController,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController vinController;
  final TextEditingController customerIdController;
  final TextEditingController occasionController;
  final TextEditingController milageController;

  final TextEditingController firstNameController;
  final TextEditingController lastNameController;

  final TextEditingController phoneController;
  final TextEditingController emailController;
  final TextEditingController zipcodeController;
  final TextEditingController cityController;
  final TextEditingController streetController;
  final TextEditingController housenumberController;

  @override
  State<AddCaseDialogForm> createState() => _AddCaseDialogFormState();

  static Future<bool?> _showConfirmSelectCustomerDialog(
    BuildContext context,
    String value,
  ) {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(tr("cases.addCaseDialog.confirmDialog.title")),
          content: Text(
            tr(
              "cases.addCaseDialog.confirmDialog.description",
              namedArgs: {"customer": value},
            ),
          ),
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

class _AddCaseDialogFormState extends State<AddCaseDialogForm> {
  bool showAddCustomerFields = false;

  // TODO replace with actual data
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
          key: widget.formKey,
          child: SizedBox(
            width: 400,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    SizedBox(
                      width: 227,
                      child: TextFormField(
                        inputFormatters: [UpperCaseTextInputFormatter()],
                        decoration: InputDecoration(
                          labelText: tr("general.vehicleVin"),
                          border: const OutlineInputBorder(),
                        ),
                        controller: widget.vinController,
                        onSaved: (vin) {
                          if (vin == null) {
                            throw AppException(
                              exceptionType: ExceptionType.unexpectedNullValue,
                              exceptionMessage:
                                  "VIN was null, validation failed.",
                            );
                          }
                          if (vin.isEmpty) {
                            throw AppException(
                              exceptionType: ExceptionType.unexpectedNullValue,
                              exceptionMessage:
                                  "VIN was empty, validation failed.",
                            );
                          }
                        },
                        validator: (String? value) {
                          if (value == null || value.isEmpty) {
                            return tr("general.obligatoryField");
                          }
                          if (value.contains(RegExp("[IOQ]"))) {
                            return tr(
                                "cases.addCaseDialog.vinCharactersInvalid");
                          }
                          if (value.length != 17) {
                            return tr("cases.addCaseDialog.vinLengthInvalid");
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    SizedBox(
                      width: 157,
                      child: TextFormField(
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly
                        ],
                        controller: widget.milageController,
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
                        onSaved: (value) {
                          if (value == null) {
                            throw AppException(
                              exceptionType: ExceptionType.unexpectedNullValue,
                              exceptionMessage:
                                  "Milage was null, validation failed.",
                            );
                          }
                          if (value.isEmpty) {
                            throw AppException(
                              exceptionType: ExceptionType.unexpectedNullValue,
                              exceptionMessage:
                                  "Milage was empty, validation failed.",
                            );
                          }
                        },
                      ),
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
                      initialValue: CaseOccasion.fromString(
                        widget.occasionController.text,
                      ),
                      onSaved: (CaseOccasion? newValue) {
                        if (newValue == null) {
                          throw AppException(
                            exceptionType: ExceptionType.unexpectedNullValue,
                            exceptionMessage: "Occasion was null.",
                          );
                        }
                        widget.occasionController.text =
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
                              widget.occasionController.text =
                                  EnumToString.convertToString(newVal);
                              field.didChange(newVal);
                            },
                          ),
                        );
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Tooltip(
                      message: tr("cases.addCaseDialog.customerTooltip"),
                      child: DropdownMenu<String>(
                        enabled: !showAddCustomerFields,
                        label: Text(tr("general.customer")),
                        hintText: tr("forms.optional"),
                        enableFilter: true,
                        width: 320,
                        menuHeight: 350,
                        onSelected: (value) async =>
                            _onCustomerSelection(context, value),
                        menuStyle:
                            const MenuStyle(alignment: Alignment.bottomLeft),
                        // TODO replace mock data with adjusted customerModels
                        dropdownMenuEntries:
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
                    const SizedBox(width: 20),
                    if (showAddCustomerFields)
                      Tooltip(
                        message: tr(
                          "cases.addCaseDialog.cancelCreateNewCustomerTooltip",
                        ),
                        child: IconButton(
                          icon: const Icon(Icons.cancel),
                          onPressed: () {
                            showAddCustomerFields = false;
                            setState(() {});
                          },
                        ),
                      )
                    else
                      Tooltip(
                        message: tr(
                          "cases.addCaseDialog.createNewCustomerTooltip",
                        ),
                        child: IconButton(
                          icon: const Icon(Icons.person_add),
                          onPressed: () {
                            showAddCustomerFields = true;
                            setState(() {});
                          },
                        ),
                      ),
                  ],
                ),
                if (showAddCustomerFields)
                  ...buildWidgetsForCreatingNewCustomer()
              ],
            ),
          ),
        );
      },
    );
  }

  List<Widget> buildWidgetsForCreatingNewCustomer() {
    return [
      const SizedBox(height: 16),
      Row(
        children: [
          SizedBox(
            width: 192,
            child: TextFormField(
              controller: widget.firstNameController,
              decoration: InputDecoration(
                labelText: tr("general.firstname"),
                border: const OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return tr("general.obligatoryField");
                }
                return null;
              },
              onSaved: (value) {
                if (value == null) {
                  throw AppException(
                    exceptionType: ExceptionType.unexpectedNullValue,
                    exceptionMessage: "First name was null, validation failed.",
                  );
                }
                if (value.isEmpty) {
                  throw AppException(
                    exceptionType: ExceptionType.unexpectedNullValue,
                    exceptionMessage:
                        "First name was empty, validation failed.",
                  );
                }
              },
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 192,
            child: TextFormField(
              controller: widget.lastNameController,
              decoration: InputDecoration(
                labelText: tr("general.lastname"),
                border: const OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return tr("general.obligatoryField");
                }
                return null;
              },
              onSaved: (value) {
                if (value == null) {
                  throw AppException(
                    exceptionType: ExceptionType.unexpectedNullValue,
                    exceptionMessage: "Last name was null, validation failed.",
                  );
                }
                if (value.isEmpty) {
                  throw AppException(
                    exceptionType: ExceptionType.unexpectedNullValue,
                    exceptionMessage: "Last name was empty, validation failed.",
                  );
                }
              },
            ),
          ),
        ],
      ),
      const SizedBox(height: 16),
      Row(
        children: [
          SizedBox(
            width: 192,
            child: TextFormField(
              // TODO add email validator
              controller: widget.emailController,
              decoration: InputDecoration(
                labelText: tr("general.email"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 192,
            child: TextFormField(
              controller: widget.phoneController,
              decoration: InputDecoration(
                labelText: tr("general.phone"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
        ],
      ),
      const SizedBox(height: 16),
      Row(
        children: [
          SizedBox(
            width: 320,
            child: TextFormField(
              controller: widget.streetController,
              decoration: InputDecoration(
                labelText: tr("general.street"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 64,
            child: TextFormField(
              controller: widget.housenumberController,
              decoration: InputDecoration(
                labelText: tr("general.housenumber"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
        ],
      ),
      const SizedBox(height: 16),
      Row(
        children: [
          SizedBox(
            width: 96,
            child: TextFormField(
              controller: widget.zipcodeController,
              decoration: InputDecoration(
                labelText: tr("general.zipcode"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 288,
            child: TextFormField(
              controller: widget.cityController,
              decoration: InputDecoration(
                labelText: tr("general.city"),
                border: const OutlineInputBorder(),
              ),
            ),
          ),
        ],
      ),
    ];
  }

  Future<void> _onCustomerSelection(
    BuildContext context,
    String? value,
  ) async {
    if (value == null) return;
    await AddCaseDialogForm._showConfirmSelectCustomerDialog(context, value)
        .then((bool? dialogResult) async {
      if (dialogResult ?? false) {
        lastSelectedCustomer = widget.customerIdController.text;
      } else {
        if (lastSelectedCustomer == null) {
          widget.customerIdController.clear();
        } else {
          widget.customerIdController.text = lastSelectedCustomer!;
        }
      }
    });
  }
}
