import "dart:async";

import "package:aw40_hub_frontend/dtos/customer_update_dto.dart";
import "package:aw40_hub_frontend/exceptions/app_exception.dart";
import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:easy_localization/easy_localization.dart";
import "package:flutter/material.dart";
import "package:routemaster/routemaster.dart";

class UpdateCustomerDialog extends StatefulWidget {
  const UpdateCustomerDialog({
    required this.customerModel,
    super.key,
  });

  final CustomerModel customerModel;

  @override
  State<UpdateCustomerDialog> createState() => _UpdateCustomerDialogState();
}

class _UpdateCustomerDialogState extends State<UpdateCustomerDialog> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController _firstNameController = TextEditingController();
  final TextEditingController _lastNameController = TextEditingController();

  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _zipcodeController = TextEditingController();
  final TextEditingController _cityController = TextEditingController();
  final TextEditingController _streetController = TextEditingController();
  final TextEditingController _housenumberController = TextEditingController();

  final title = tr("customers.actions.updateCustomer");

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    _firstNameController.text = widget.customerModel.firstname ?? "";
    _lastNameController.text = widget.customerModel.lastname ?? "";
    _phoneController.text = widget.customerModel.phone ?? "";
    _emailController.text = widget.customerModel.email ?? "";
    _zipcodeController.text = widget.customerModel.zipcode ?? "";
    _cityController.text = widget.customerModel.city ?? "";
    _streetController.text = widget.customerModel.street ?? "";
    _housenumberController.text = widget.customerModel.housenumber ?? "";

    return AlertDialog(
      title: Text(title),
      content: UpdateDialogForm(
        formKey: _formKey,
        firstNameController: _firstNameController,
        lastNameController: _lastNameController,
        phoneController: _phoneController,
        emailController: _emailController,
        streetController: _streetController,
        housenumberController: _housenumberController,
        zipcodeController: _zipcodeController,
        cityController: _cityController,
        customerModel: widget.customerModel,
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
          onPressed: _submitUpdateCustomerForm,
          child: Text(tr("general.save")),
        ),
      ],
    );
  }

  void _submitUpdateCustomerForm() {
    final FormState? currentFormKeyState = _formKey.currentState;
    if (currentFormKeyState != null && currentFormKeyState.validate()) {
      currentFormKeyState.save();

      final String firstname = _firstNameController.text;
      final String lastname = _lastNameController.text;
      final String? email =
          _emailController.text.isEmpty ? null : _emailController.text;
      final String? phone =
          _phoneController.text.isEmpty ? null : _phoneController.text;
      final String? street =
          _streetController.text.isEmpty ? null : _streetController.text;
      final String? housenumber = _housenumberController.text.isEmpty
          ? null
          : _housenumberController.text;
      final String? zipcode =
          _zipcodeController.text.isEmpty ? null : _zipcodeController.text;
      final String? city =
          _cityController.text.isEmpty ? null : _cityController.text;

      final CustomerUpdateDto customerUpdateDto = CustomerUpdateDto(
        firstname,
        lastname,
        email,
        phone,
        street,
        housenumber,
        zipcode,
        city,
      );
      unawaited(
        Routemaster.of(context).pop<CustomerUpdateDto>(customerUpdateDto),
      );
    }
  }

  Future<void> _onCancel(BuildContext context) async {
    await Routemaster.of(context).pop();
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _zipcodeController.dispose();
    _cityController.dispose();
    _streetController.dispose();
    _housenumberController.dispose();
    super.dispose();
  }
}

class UpdateDialogForm extends StatelessWidget {
  const UpdateDialogForm({
    required this.formKey,
    required this.firstNameController,
    required this.lastNameController,
    required this.phoneController,
    required this.emailController,
    required this.zipcodeController,
    required this.cityController,
    required this.streetController,
    required this.housenumberController,
    required this.customerModel,
    super.key,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController firstNameController;
  final TextEditingController lastNameController;

  final TextEditingController phoneController;
  final TextEditingController emailController;
  final TextEditingController zipcodeController;
  final TextEditingController cityController;
  final TextEditingController streetController;
  final TextEditingController housenumberController;
  final CustomerModel customerModel;

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      child: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [...buildWidgetsForUpdatingCustomer()],
        ),
      ),
    );
  }

  // TODO move this code into a dedicated widget and make controllers to params
  List<Widget> buildWidgetsForUpdatingCustomer() {
    return [
      const SizedBox(height: 16),
      Row(
        children: [
          SizedBox(
            width: 192,
            child: TextFormField(
              controller: firstNameController,
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
              controller: lastNameController,
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
              controller: emailController,
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
              controller: phoneController,
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
              controller: streetController,
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
              controller: housenumberController,
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
              controller: zipcodeController,
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
              controller: cityController,
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
}
