modify template thanks_world {
    actions replace-all-with {
        definition {
            html-help {
                <!-- insert html help text -->
            }
            implementation {
                # insert tmsh script
                puts "string_input_one = $::some_variables__string_input_one"
                puts "make_a_choice = $::some_variables__make_a_choice"
                puts "make_an_mc = $::some_variables__make_a_multi_choice"
            }
            macro {
            }
            presentation {
                # insert apl script
                section hello {
                    message say_hello "Hello Paul. You're the tops."
                }

                section some_variables {
                    string string_input_one
                    choice make_a_choice default "Neither" {"A", "B"}
                    multichoice make_a_multi_choice default {"No"} {"One", "Two", "Three", "Four"}
                }

                text {
                    some_variables.string_input_one "Enter your name."
                    some_variables.make_a_choice "Make a choice between A and B."
                    some_variables.make_a_multi_choice "Make a multiple choice."
                }
            }
            role-acl none
            run-as none
        }
    }
    description none
    ignore-verification false
    requires-bigip-version-max none
    requires-bigip-version-min none
    requires-modules none
    signing-key none
    tmpl-checksum none
    tmpl-signature none
