#!/usr/bin/perl
# Refter menu plugin for DaZeus
# Copyright (C) 2011  Aaron van Geffen <aaron@aaronweb.net>
# Original module (C) 2010  Gerdriaan Mulder <har@mrngm.com>

use strict;
use warnings;
use DaZeus;
use Time::localtime;
use XML::DOM::XPath;
use LWP::Simple;

my ($socket) = @ARGV;

if (!$socket) {
	warn "Usage: $0 socket\n";
	exit 1;
}

my $dazeus = DaZeus->connect($socket);

#####################################################################
#                       CONTROLLER FUNCTIONS
#####################################################################

my %dayToIndex = ("zo" => 0, "ma" => 1, "di" => 2, "wo" => 3, "do" => 4, "vr" => 5, "za" => 6);
my @daysOfWeek = qw(zo ma di wo do vr za zo);

$dazeus->subscribe_command("noms" => sub {
	my ($self, $network, $sender, $channel, $command, @rest) = @_;
	my ($response, $day, $noms);

	# Any specific day?
	if ($rest[0]) {
		($day, $noms) = fetchMenuByDay($rest[0]);
	}
	# Tomorrow?
	elsif (localtime->hour() >= 19) {
		$response = "Na 19 uur zijn er geen refternoms meer. Daarom krijg je de refternoms van morgen te zien ;-)\n";
		($day, $noms) = fetchMenuByDay("morgen");
	}
	# Just today, please.
	else {
		$response = "Wat heeft de Refter vandaag in de aanbieding...\n";
		($day, $noms) = fetchMenuByDay();
	}

	# There's something to eat, right?
	if (defined $noms) {
		$response .= "Eten bij de Refter op " . $day . ":\n" . $noms;
	}
	# No noms whatsoever?! THE AGONY!
	else {
		$response .= "Helaas, er is niks :'-(";
	}

	# Send it in the appropriate manner.
	if ($channel eq $dazeus->getNick($network)) {
		$dazeus->message($network, $sender, $response);
	} else {
		$dazeus->message($network, $channel, $response);
	}
});

while($dazeus->handleEvents()) {}

#####################################################################
#                          MODEL FUNCTIONS
#####################################################################

sub getDayKey {
	my ($day) = @_;

	# The #ru regulars like their puns, so let's shorten this.
	$day = lc(substr($day, 0, 2)) if($day);

	# A specific request!
	if ($day and exists $dayToIndex{$day}) {
		return $dayToIndex{$day};
	}
	# Tomorrow ("morgen")
	elsif ($day eq "mo") {
		return (localtime->wday() + 1) % 7;
	}
	# The day after tomorrow ("overmorgen")
	elsif ($day eq "ov") {
		return (localtime->wday() + 2) % 7;
	}
	# Just today.
	else {
		return localtime->wday();
	}
}

# NOTE: this sub assumes $day to be an integer in [0..6]
sub pickMenuUrl {
	my ($day) = @_;

	my $next_week = localtime->wday() > $day;
	# except when it's sunday, then always take next week
	$next_week = 1 if(localtime->wday() == 0);

	return "http://www.ru.nl/facilitairbedrijf/horeca/refter-0/weekmenu-refter/menu-" . ($next_week ? "komende" : "deze") . "-week/?rss=true";
}

sub fetchMenuByDay {
	my ($day) = @_;
	my $tree = XML::DOM::Parser->new();

	$day = getDayKey($day);

	my $doc = $tree->parse(get(pickMenuUrl($day)));
	my ($menu_day, $menu);

	foreach ($doc->findnodes('//item')) {
		# The title is used to determine whether we have the right day.
		my $title = $_->getElementsByTagName('title')->item(0)->getFirstChild()->getNodeValue();

		# If this item is not relevant to the query, skip it.
		if ($day != $dayToIndex{lc(substr($title, 0, 2))}) {
			next;
		}

		# What day is it, again?
		$menu_day = lc(($title =~ /([A-z]+dag \d+ [a-z]+):?/)[0]);

		# Fetch the menu for the day.
		$menu = $_->getElementsByTagName('description')->item(0)->getFirstChild()->getNodeValue();

		# Perchance there's additional price info -- we already know!
		$menu =~ s/Prijs\s*:[^\n]*\n//s;

		# Trim any leading and trailing whitespace.
		$menu =~ s/^\s+(.+?)\s+$/$1/s;

		# Strip superfluous information
		$menu =~ s/\(\s*['`]s[ -]avonds\s*\)\s?//;

		last;
	}

	if (!defined $menu_day) {
		$menu_day = $daysOfWeek[$day];
	}

	return ($menu_day, $menu);
}
