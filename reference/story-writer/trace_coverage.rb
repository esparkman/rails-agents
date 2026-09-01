#!/usr/bin/env ruby
# frozen_string_literal: true
# Requirements -> test traceability. Maps each story business_rule id to the test(s)
# that DECLARE they cover it, so coverage is data, not a grep guess (the E2-miss guard).
#
#   ruby trace_coverage.rb <stories_dir> <test_dir>
#   exit 0 = every rule covered, 1 = gaps, 2 = bad args
#
# Convention: a test annotates what it proves with a comment `# covers: <rule-id>`
# (one per behavior). e.g.  test "rejects a price below the floor" do  # covers: C3-min-price
# Until tests adopt the annotation, rules show as GAP — that IS the traceability gap,
# surfaced honestly rather than assumed away.

require "yaml"

stories, tests = ARGV[0], ARGV[1]
abort "usage: trace_coverage.rb <stories_dir> <test_dir>" unless stories && tests && File.directory?(stories) && File.directory?(tests)

rules = {}
Dir.glob(File.join(stories, "*.yaml")).each do |f|
  doc = begin YAML.safe_load(File.read(f), permitted_classes: [Symbol]); rescue; next; end
  next unless doc.is_a?(Hash)
  Array(doc["business_rules"]).each do |r|
    rules[r["id"].to_s] = doc["id"] if r.is_a?(Hash) && r["id"]
  end
end
abort "no business_rule ids found in #{stories}" if rules.empty?

covers = Hash.new { |h, k| h[k] = [] }
Dir.glob(File.join(tests, "**", "*.rb")).each do |tf|
  File.foreach(tf) do |line|
    line.scan(/covers:\s*([A-Za-z0-9_.\-]+)/) { |m| covers[m[0]] << File.basename(tf) }
  end
end

covered = 0
puts "RULE".ljust(26) + "CARD  STATUS   TEST"
rules.sort.each do |id, card|
  hit = covers[id].uniq
  if hit.any?
    covered += 1
    puts id.ljust(26) + "#{card.to_s.ljust(5)} COVERED  #{hit.join(', ')}"
  else
    puts id.ljust(26) + "#{card.to_s.ljust(5)} GAP      (no test declares 'covers: #{id}')"
  end
end
gaps = rules.size - covered
puts "\n#{covered}/#{rules.size} rules covered; #{gaps} gap(s)."
exit(gaps.zero? ? 0 : 1)
