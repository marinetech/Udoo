#!/usr/bin/expect  --
# Copyright (c) 2016 Regents of the SIGNET lab, University of Padova.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University of Padova (SIGNET lab) nor the 
#    names of its contributors may be used to endorse or promote products 
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED 
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Filippo Campagnaro
# email: campagn1@dei.unipd.it
# place it in /usr/local/bin/upload_files.tcl
# Breif description: script to upload files of an user
set remote_user "service"
set pass "tabsbuoy"
set host "165.91.230.239"
set remote_folder "/home/data/mainland/"
set uploads_folder "files2upload"
set uploaded_folder "files_uploaded"
set timeout 10

if {$argc != 1} {
    puts "The script requires one input:"
    puts "- user_name"
    puts "example: ./uwcbr.tcl udooer"
    puts "Please try again."
    return
} else {
    set user_name [lindex $argv 0]
}

set curr_date [eval exec /bin/date +%s]
set my_name [eval exec /bin/hostname]
set my_id [eval exec /usr/bin/hostid]
exec /usr/bin/7z a /home/$user_name/$uploads_folder/${my_name}${my_id}_$curr_date.7z /home/$user_name/$uploads_folder/

spawn bash -c "/usr/bin/scp /home/$user_name/$uploads_folder/*.7z $remote_user@${host}:${remote_folder}."
expect {           
    -re ".*password:" {
        send "$pass\r"
        set timeout -1
	    exp_continue
    } -re ".*yes/no.*" {
        send "yes\r"
        set timeout -1
        exp_continue
    } timeout {

    } -re  {
        exp_continue
    } eof {
      
    }
}

foreach file [glob -nocomplain /home/$user_name/$uploads_folder/*] {
  file copy -force -- $file [file join /home/$user_name/$uploaded_folder/.]
  sleep 0.1
  file delete -force -- $file
}

exit
