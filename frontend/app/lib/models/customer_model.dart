class CustomerModel {
  CustomerModel({
    required this.id,
    this.firstname,
    this.lastname,
    this.email,
    this.phone,
    this.street,
    this.housenumber,
    this.postcode,
    this.city,
  });
  // TODO make firstname and lastname (and Id?) required
  String? id;
  String? firstname;
  String? lastname;
  String? email;
  String? phone;
  String? street;
  String? housenumber;
  String? postcode;
  String? city;
}
