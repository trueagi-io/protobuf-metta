# Protobuf parser.  Outputs a string in MeTTa format for now.

class ProtobufParser:
    """Protobuf parser"""

    def __init__(self, desc, prefix:str="", curried:bool=False):
        # Set protobuf DESCRIPTOR object
        self.descriptor = desc

        # Set prefix, a string to be prepended before every MeTTa
        # symbol to guaranty uniqness.  If no such prefix is provided
        # then fall back on package.
        self.prefix = prefix if prefix else self.descriptor.package
        self.prefix_dot = self.prefix + "."

        # Set curried.  If True then all type signatures are curried,
        # meaning (-> T1 T2 T3) is turned into (-> T1 (-> T2 T3))
        self.curried = curried

        # Protobuf type name indices
        self.TYPE_DOUBLE = 1
        self.TYPE_FLOAT = 2
        self.TYPE_INT64 = 3
        self.TYPE_UINT64 = 4
        self.TYPE_INT32 = 5
        self.TYPE_FIXED64 = 6
        self.TYPE_FIXED32 = 7
        self.TYPE_BOOL = 8
        self.TYPE_STRING = 9
        self.TYPE_GROUP = 10
        self.TYPE_MESSAGE = 11
        self.TYPE_BYTES = 12
        self.TYPE_UINT32 = 13
        self.TYPE_ENUM = 14
        self.TYPE_SFIXED32 = 15
        self.TYPE_SFIXED64 = 16
        self.TYPE_SINT32 = 17
        self.TYPE_SINT64 = 18

        # Map protobuf type indices to MeTTa type names
        self.type_names = {
            self.TYPE_DOUBLE : "Double",
            self.TYPE_FLOAT : "Float",
            self.TYPE_INT64 : "Int64",
            self.TYPE_UINT64 : "UInt64",
            self.TYPE_INT32 : "Int32",
            self.TYPE_FIXED64 : "Fixed64",
            self.TYPE_FIXED32 : "Fixed32",
            self.TYPE_BOOL : "Bool",
            self.TYPE_STRING : "String",
            self.TYPE_GROUP : "Group",
            self.TYPE_MESSAGE : "Message",
            self.TYPE_BYTES : "Bytes",
            self.TYPE_UINT32 : "UInt32",
            self.TYPE_ENUM : "Enum",
            self.TYPE_SFIXED32 : "SFixed32",
            self.TYPE_SFIXED64 : "SFixed64",
            self.TYPE_SINT32 : "SInt32",
            self.TYPE_SINT64 : "SInt64"
        }

    def description_to_metta(self) -> str:
        """Parse the protobuf description provided in the constructor"""

        # MeTTa file header
        desc_rep : str = ""
        desc_rep += ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
        desc_rep += ";; MeTTa representation, generated by protobuf-metta\n"
        desc_rep += ";;\n"
        desc_rep += f";; Protobuf file: {self.descriptor.name}\n"
        desc_rep += f";; Protobuf syntax: {self.descriptor.syntax}\n"
        if self.descriptor.package:
            desc_rep += f";; Protobuf package: {self.descriptor.package}\n"
        if self.prefix:
            desc_rep += f";; Prefix: {self.prefix}\n"
        desc_rep += ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
        desc_rep += "\n"

        # Parse messages
        desc_rep += ";;;;;;;;;;;;;;;;;;;\n"
        desc_rep += ";; Message Types ;;\n"
        desc_rep += ";;;;;;;;;;;;;;;;;;;\n\n"
        for msg_name, msg in self.descriptor.message_types_by_name.items():
            msg_name_len = len(msg_name)
            desc_rep += ";;;" + msg_name_len * ";" + ";;;\n"
            desc_rep += f";; {msg_name} ;;\n"
            desc_rep += ";;;" + msg_name_len * ";" + ";;;\n\n"
            desc_rep += self.message_to_metta(msg)

        # Parse enums

        # Parse services
        desc_rep += ";;;;;;;;;;;;;;\n"
        desc_rep += ";; Services ;;\n"
        desc_rep += ";;;;;;;;;;;;;;\n\n"
        for srv_name, srv in self.descriptor.services_by_name.items():
            srv_name_len = len(srv_name)
            desc_rep += ";;;" + srv_name_len * ";" + ";;;\n"
            desc_rep += f";; {srv_name} ;;\n"
            desc_rep += ";;;" + srv_name_len * ";" + ";;;\n\n"
            desc_rep += self.service_to_metta(srv)

        return desc_rep

    def field_type_to_metta(self, field) -> str:
        """Parse a field type, return its representation in MeTTa format."""

        if field.type == self.TYPE_MESSAGE:
            return self.prefix_dot + field.message_type.name
        if field.type == self.TYPE_ENUM:
            return self.prefix_dot + field.enum_type.name
        return self.type_names[field.type]

    def enum_to_metta(self, enm) -> str:
        """Parse enum type, output corresponding string MeTTa format.

        Example:

        Assuming a package `example`, the protobuf enum specification

        ```
        enum Week {
          SUN = 0;
          MON = 1;
          TUE = 2;
          WED = 3;
          THU = 4;
          FRI = 5;
          SAT = 6;
        }
        ```

        outputs the following string in MeTTa format

        ```
        ;; Define example.Week type
        (: example.Week Type)

        ;; Define example.Week enum values
        (: example.Week.SUN example.Week)
        (: example.Week.MON example.Week)
        (: example.Week.TUE example.Week)
        (: example.Week.WED example.Week)
        (: example.Week.THU example.Week)
        (: example.Week.FRI example.Week)
        (: example.Week.SAT example.Week)
        ```

        For now enum numbers are discarded from the MeTTa format.

        """

        # Enum string representation in MeTTa format
        enm_rep : str = ""

        # Type declaration
        enm_class_name : str = self.prefix_dot + enm.name
        enm_rep += f";; Define {enm_class_name} enum type\n"
        enm_rep += f"(: {enm_class_name} Type)\n\n"

        # Enum values
        enm_rep += f";; Define {enm_class_name} enum values\n"
        for enm_name, enm_value in enm.values_by_name.items():
            enm_rep += "(: {0}.{1} {0})\n".format(enm_class_name, enm_name)
        enm_rep += "\n"

        return enm_rep

    def message_to_metta(self, msg) -> str:

        """Parse message type, output corresponding string in MeTTa format.

        Example:

        Assuming a package `example`, the protobuf message specification

        ```
        message Name {
          string forename = 1;
          string surname = 2;
        }
        ```

        outputs the following string in MeTTa format

        ```
        ;; Define example.Name type
        (: example.Name Type)

        ;; Define example.Name constructor
        (: example.MkName
           (->
            String ; forename
            String ; surname
            example.Name))

        ;; Define example.Name access functions

        ;; Access function of forename
        (: example.Name.forename (-> example.Name String))
        (= (example.Name.forename
             (example.MkName
               $forename
               $surname
             )
           )
           $forename)

        ;; Access function of surname
        (= (example.Name.surname
             (example.MkName
               $forename
               $surname
             )
           )
           $surname)
        ```

        If self.curried has been set to True then

        ```
        ;; Define example.Name constructor
        (: example.MkName
           (->
            String ; forename
            String ; surname
            example.Name))
        ```

        will look like

        ```
        ;; Define example.Name constructor
        (: example.MkName
           (-> String ; forename
               (-> String ; surname
                   example.Name)))
        ```

        """

        # Message string representation in MeTTa format
        msg_rep : str = ""

        # Type declaration
        class_name : str = self.prefix_dot + msg.name
        msg_rep += f";; Define {class_name} type\n"
        msg_rep += f"(: {class_name} Type)\n\n"

        # Nested message type declarations
        for nested_msg_name, nested_msg in msg.nested_types_by_name.items():
            msg_rep += self.message_to_metta(nested_msg)

        # Nested enum type declarations
        for nested_enm_name, nested_enm in msg.enum_types_by_name.items():
            msg_rep += self.enum_to_metta(nested_enm)

        # Type constructor
        ctor_name : str = f"{self.prefix_dot}Mk{msg.name}"
        msg_rep += f";; Define {class_name} constuctor\n"
        msg_rep += f"(: {ctor_name}\n"
        if self.curried:
            field_cnt = 0       # Different than field_num because it
                                # does not take into account the
                                # protobuf field index.
            indent = 3*" "      # Space indentation to be place in
                                # front of "(-> T"
            for field_num, field in msg.fields_by_number.items():
                type_name : str = self.field_type_to_metta(field)
                msg_rep += f"{indent}(-> {type_name} ; {field.name}\n"
                indent += 4*" "
                field_cnt += 1
            msg_rep += f"{indent}{class_name}{field_cnt*')'})\n"
        else:
            msg_rep += "   (->\n"
            for field_num, field in msg.fields_by_number.items():
                type_name : str = self.field_type_to_metta(field)
                msg_rep += f"    {type_name} ; {field.name}\n"
            msg_rep += f"    {class_name}))\n\n"

        # Access functions
        field_names = [field.name for _, field in msg.fields_by_number.items()]
        msg_rep += f";; Define {class_name} access functions\n\n"
        for field_num, field in msg.fields_by_number.items():
            fn_name : str = f"{class_name}.{field.name}"
            type_name : str = self.field_type_to_metta(field)
            msg_rep += f";; Define {fn_name}\n"
            msg_rep += f"(: {fn_name}\n"
            msg_rep += f"   (-> {class_name} {type_name}))\n"
            msg_rep += f"(= ({fn_name}\n"
            msg_rep += f"    ({ctor_name}\n"
            msg_rep += "\n".join([f"     ${fn}" for fn in field_names])
            msg_rep += ")) ${field.name})\n\n"

        return msg_rep

    def service_to_metta(self, srv) -> str:
        """Parse service, output corresponding string in MeTTa format.

        Example:

        Assuming a package `example`, the protobuf service specification

        ```
        service Greeter {
          rpc salute (Person) returns (Greet) {}
          rpc wish (Person) returns (Greet) {}
        }
        ```

        outputs the following string in MeTTa format

        ```
        ;; Define example.Greeter.salute service method
        (: example.Greeter.salute
           (-> Person Greet))

        ;; Define example.Greeter.wish service method
        (: example.Greeter.wish
           (-> Person Greet))
        ```

        """

        # Service string representation in MeTTa format
        srv_rep : str = ""

        # Service methods
        for mtd_name, mtd in srv.methods_by_name.items():
            pfx_mtd_name = self.prefix_dot + mtd_name
            pfx_input_name = self.prefix_dot + mtd.input_type.name
            pfx_output_name = self.prefix_dot + mtd.output_type.name
            srv_rep += f";; Define {pfx_mtd_name} service method\n"
            srv_rep += f"(: {pfx_mtd_name}\n"
            srv_rep += f"   (-> {pfx_input_name} {pfx_output_name}))\n\n"
        return srv_rep
