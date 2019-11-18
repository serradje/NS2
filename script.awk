BEGIN  {count=0; SEND_NODE=0; DEST_NODE=1; FLOW=0}
$1 == "-" { if ($3 == SEND_NODE && $4 == DEST_NODE && $6 >= 1000 && $8 == FLOW) {
               count++;
            }
          }

$1 == "d" { if ($3 == SEND_NODE && $4 == DEST_NODE) {
               drop++;
            }
          }
END    {print count;
	print drop;
}

