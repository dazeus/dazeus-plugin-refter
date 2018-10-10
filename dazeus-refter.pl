#!/usr/bin/perl
# Refter menu plugin for DaZeus
# Copyright (C) 2011-2017  Aaron van Geffen <aaron@aaronweb.net>
# Original module (C) 2010  Gerdriaan Mulder <har@mrngm.com>

use strict;
use warnings;
use DaZeus;
use Time::localtime;
use LWP::Simple;

my $socket = shift;
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

$dazeus->subscribe_command("noms" => \&fetchMenu);
$dazeus->subscribe_command("refter" => \&fetchMenu);

while($dazeus->handleEvents()) {}

sub fetchMenu {
	my ($self, $network, $sender, $channel, $command, $rest) = @_;
	my ($response, $day, $noms);

	# Any specific day?
	if ($rest) {
		($day, $noms) = processMenuFeed($rest);
	}
	# Tomorrow?
	elsif (localtime->hour() >= 19) {
		$response = "Na 19 uur zijn er geen gerechten meer. Daarom krijg je de gerechten van morgen te zien ;-)\n";
		($day, $noms) = processMenuFeed("morgen");
	}
	# Just today, please.
	else {
		$response = "Wat heeft het Gerecht vandaag in de aanbieding...\n";
		($day, $noms) = processMenuFeed();
	}

	# There's something to eat, right?
	if (defined $noms) {
		$response .= "Eten bij het Gerecht op " . $day . ":\n" . $noms;
	}
	# No noms whatsoever?! THE AGONY!
	else {
		$response .= "Helaas, er is niks :'-(";
	}

	# Send it in the appropriate manner.
	$self->reply($response, $network, $sender, $channel);
}


#####################################################################
#                          MODEL FUNCTIONS
#####################################################################


sub getDayKey {
	my $day = shift;

	if (!defined($day)) {
		return localtime->wday();
	}

	# The #ru regulars like their puns, so let's shorten this.
	$day = lc(substr($day, 0, 2));

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
	my $day = shift;

	my $next_week = localtime->wday() > $day;
	# except when it's sunday, then always take next week
	$next_week = 1 if(localtime->wday() == 0);

	#my $url = "http://www.ru.nl/facilitairbedrijf/horeca/de-refter/weekmenu-refter/menu-soep-" . ($next_week ? "komende" : "deze") . "-week/";
	my $url = "https://www.ru.nl/facilitairbedrijf/horeca/het-gerecht-grotiusgebouw/menu-8-12-oktober/";
	print "[refter][" . CORE::localtime() . "] Fetching menu from ", $url, "\n";
	return $url;
}

sub processMenuFeed {
	my $day = shift;
	$day = getDayKey($day);

	# Load the relevant menu page.
	my $page = get(pickMenuUrl($day));
	if (!defined $page) {
		return (undef, undef);
	}

	# Extract the relevant layer from the page.
	my $menu_container;
	if ($page =~ m!<div class="iprox-rich-content iprox-content">(.+?)<\/div>!s) {
		$menu_container = $1;
	} else {
		return (undef, undef);
	}

	# Iterate over day menus.
	while ($menu_container =~ m!<p><strong>(.+?)</strong><\/p>\s*<ul>\s*((?:<li><span[^>]*>[^<]+?<\/span>\s*)*)</ul>!sg) {
		my $menu_day = $1;
		my $menu_items = $2;

		# If this is not the menu for day we were looking for, continue...
		if ($day != $dayToIndex{lc(substr($menu_day, 0, 2))}) {
			next;
		}

		# Otherwise, enumerate the menu!
		my $menu = "";
		while ($menu_items =~ m!<li><span[^>]*>([^<]+?)<\/span>!sg) {
			$menu .= $1 . "\n";
		}

		# And return it!
		return ($menu_day, $menu);
	}

	# Apparently, we did not find a match.
	return (undef, undef);
}
