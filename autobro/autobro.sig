signature auto-bro-3224{
	ip-proto == tcp
	event "auto-bro-3224: Attack succeded :-("
	requires-reverse-signature auto-bro-3222
	payload /.*1.*/

}
signature auto-bro-3222{
	dst-port == 3632
	ip-proto == tcp
	event "auto-bro-3222: Attack attempt"
	payload /.*DIST00000001ARGC00000008ARGV00000002shARGV00000002-cARGV000000.*/

}
signature auto-bro-3284{
	ip-proto == tcp
	event "auto-bro-3284: Attack succeded :-("
	requires-reverse-signature auto-bro-3282
	payload /.*\x32\x32\x30\x20\x6c.*\x6f.*/

}
signature auto-bro-3282{
	dst-port == 25
	ip-proto == tcp
	event "auto-bro-3282: Attack attempt"
	payload /.*\x6c.*\x20.*\x73.*/

}
