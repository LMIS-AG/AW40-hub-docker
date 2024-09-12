import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:json_annotation/json_annotation.dart";

part "customer_dto.g.dart";

@JsonSerializable()
class CustomerDto {
  CustomerDto(
    this.id,
    this.firstname,
    this.lastname,
    this.email,
    this.phone,
    this.street,
    this.housenumber,
    this.zipcode,
    this.city,
  );

  factory CustomerDto.fromJson(Map<String, dynamic> json) {
    return _$CustomerDtoFromJson(json);
  }
  Map<String, dynamic> toJson() => _$CustomerDtoToJson(this);

  CustomerModel toModel() {
    return CustomerModel(
      id: id,
      firstname: firstname,
      lastname: lastname,
      email: email,
      phone: phone,
      street: street,
      housenumber: housenumber,
      zipcode: zipcode,
      city: city,
    );
  }

  @JsonKey(name: "_id")
  AnonymousCustomerId id;
  // TODO make firstname and lastname required
  @JsonKey(name: "first_name")
  String? firstname;
  @JsonKey(name: "last_name")
  String? lastname;
  String? email;
  String? phone;
  String? street;
  @JsonKey(name: "house_number")
  String? housenumber;
  // TODO maybe rename into postcode
  @JsonKey(name: "postcode")
  String? zipcode;
  String? city;
}
