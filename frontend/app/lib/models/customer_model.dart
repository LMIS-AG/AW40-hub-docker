import "package:aw40_hub_frontend/utils/enums.dart";

class CustomerModel {
  CustomerModel({
    required this.id,
    this.firstname,
    this.lastname,
    this.email,
    this.phone,
    this.street,
    this.housenumber,
    this.zipcode,
    this.city,
  });
  AnonymousCustomerId id;
  // TODO make firstname and lastname required
  String? firstname;
  String? lastname;
  String? email;
  String? phone;
  String? street;
  String? housenumber;
  String? zipcode;
  String? city;
}
