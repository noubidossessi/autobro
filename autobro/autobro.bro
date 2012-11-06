
# autobro site configuration

@load udp
@load weird
@load notice
@load alarm
@load signatures
#@load local

redef capture_filters += {["tcp"] = "tcp"} ;
redef signature_files += "autobro.sig" ;
redef ignore_checksums = T;
redef dpd_match_only_beginning = F;
redef dpd_buffer_size = 1048576;

event signature_match (state: signature_state, msg: string, data: string)
    {
        local id = state$id ;
        local is_orig: bool = state$is_orig ;
        local payload_size: count = state$payload_size ;

        local f:file = open_for_append("sucesses.log");
        local g:file = open_for_append("attempts.log");
        local text: string = fmt("%s", msg) ;
        local orig_h = state$conn$id$orig_h;
        local orig_p = state$conn$id$orig_p;
        local resp_h = state$conn$id$resp_h;
        local resp_p = state$conn$id$resp_p;
        local log_file:file;

        if (is_orig)
            {
                log_file = g;
            }
        else
            {
                log_file = f;
            }
        print log_file, text;
        print log_file, fmt( "    Destination address: %s", resp_h);
        print log_file, fmt( "    Destination port: %s", resp_p);
        print log_file, fmt( "    Source address: %s", orig_h );
        print log_file, fmt( "    Source port:: %s" , orig_p);


    }
