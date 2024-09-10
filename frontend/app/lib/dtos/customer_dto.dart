import "package:aw40_hub_frontend/models/customer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:json_annotation/json_annotation.dart";

part "customer_dto.g.dart";

@JsonSerializable()
class CustomerDto {
  CustomerDto(
    this.id,
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
  String? firstname;
  String? lastname;
  String? email;
  String? phone;
  String? street;
  String? housenumber;
  String? zipcode;
  String? city;
}
