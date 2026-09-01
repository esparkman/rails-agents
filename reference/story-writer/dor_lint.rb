#!/usr/bin/env ruby
# frozen_string_literal: true

# Definition-of-Ready gate for Story Writer inputs.
# Deterministic poka-yoke: a story YAML either PASSES or is NOT-READY with the
# exact gaps named. The DoR verdict is COMPUTED here, never self-asserted by the
# author. Stdlib only — no gems, so it runs anywhere.
#
#   ruby dor_lint.rb story.yaml        # exit 0 = PASSED, 1 = NOT-READY, 2 = malformed

require "yaml"

VAGUE_TERMS = %w[
  positive negative valid invalid correct incorrect appropriate reasonable
  proper nice fast quick snappy slow good better best pretty prettier
  clean weird robust scalable efficient intuitive seamless modern simple
  several some various roughly approximately handful many few
  soon eventual manageable enough awhile sometime ongoing periodic
  occasional sizable lots plenty
].freeze

# Multi-word vagueness a single-word scan misses. Unambiguous duration/quantity hedges.
VAGUE_PHRASES = ["a while", "some time", "a bit", "a lot", "a few", "and so on", "etc", "as needed", "or so"].freeze

OUTCOME_TYPES = %w[rendered redirect email db_change validation_error flash].freeze
THRESHOLD = /(>=|<=|>|<|minimum|maximum|at least|at most|greater than|less than|no more than|no less than)/i

class Lint
  def initialize(doc)
    @doc = doc
    @violations = []
  end

  def run
    return fail_structure unless @doc.is_a?(Hash)
    # Every check is nil/empty-safe, so run them all and report every gap at once
    # (a refinement list, not one-at-a-time whack-a-mole).
    check_required
    check_source
    check_out_of_scope
    check_business_rules
    check_acceptance_criteria
    check_coverage
    check_thresholds
    check_vague
    check_open_questions
    report
  end

  private

  def v(msg) = @violations << msg

  def check_required
    # Presence only. Array-emptiness is reported by the dedicated checks below,
    # with a more useful message, so we don't double-flag it here.
    %w[id title source operator goal].each do |k|
      val = @doc[k]
      v("missing required field: #{k}") if val.nil? || val.to_s.strip.empty?
    end
    %w[business_rules acceptance_criteria out_of_scope].each do |k|
      v("missing required field: #{k}") if @doc[k].nil?
    end
  end

  def check_source
    v("source is present but empty — cite the authority (e.g. 'AWDWR C3')") if @doc["source"].to_s.strip.empty?
  end

  def check_out_of_scope
    v("out_of_scope must be non-empty — state exclusions explicitly (prevents scope creep)") if Array(@doc["out_of_scope"]).empty?
  end

  def rules = Array(@doc["business_rules"])
  def acs   = Array(@doc["acceptance_criteria"])

  def check_business_rules
    v("business_rules must be non-empty — a story with no rules cannot be graded") if rules.empty?
    rules.each_with_index do |r, i|
      v("business_rules[#{i}] must have an 'id'") if r["id"].to_s.strip.empty?
      v("business_rules[#{i}] must have a 'predicate'") if r["predicate"].to_s.strip.empty?
    end
  end

  def check_acceptance_criteria
    v("acceptance_criteria must be non-empty — each rule needs observable proof") if acs.empty?
    acs.each_with_index do |a, i|
      %w[given when then covers outcome_type].each do |k|
        v("acceptance_criteria[#{i}] missing '#{k}'") if a[k].nil? || (a[k].respond_to?(:empty?) && a[k].empty?)
      end
      ot = a["outcome_type"]
      v("acceptance_criteria[#{i}] outcome_type '#{ot}' not in #{OUTCOME_TYPES.join('/')}") if ot && !OUTCOME_TYPES.include?(ot)
    end
  end

  def check_coverage
    covered = acs.flat_map { |a| Array(a["covers"]) }.to_set
    rules.each do |r|
      id = r["id"].to_s
      next if id.empty?
      v("business_rule '#{id}' has no acceptance_criteria covering it") unless covered.include?(id)
    end
  end

  def check_thresholds
    counts = Hash.new(0)
    acs.each { |a| Array(a["covers"]).each { |c| counts[c] += 1 } }
    rules.each do |r|
      next unless r["predicate"].to_s.match?(THRESHOLD) && r["predicate"].to_s.match?(/\d/)
      if counts[r["id"].to_s] < 2
        v("business_rule '#{r['id']}' is a threshold — needs >=2 ACs (the boundary AND just-outside it)")
      end
    end
  end

  def check_vague
    scan = []
    scan << ["goal", @doc["goal"].to_s]
    rules.each { |r| scan << ["business_rule '#{r['id']}' predicate", r["predicate"].to_s] }
    acs.each_with_index { |a, i| %w[given when then].each { |k| scan << ["acceptance_criteria[#{i}].#{k}", a[k].to_s] } }

    scan.each do |where, text|
      next if text.match?(/\d/) # a concrete number qualifies the statement
      # suffix-tolerant so inflections are caught too (appropriate->appropriately, old->older, quick->quickly)
      dc = text.downcase
      hits = VAGUE_TERMS.select { |t| dc.match?(/\b#{Regexp.escape(t)}(?:s|d|r|ly|st|er|est|ing|ness)?\b/) }
      hits += VAGUE_PHRASES.select { |p| dc.include?(p) }
      v("vague term(s) #{hits.inspect} in #{where}: \"#{text}\" — replace with a concrete value/enumeration") if hits.any?
    end
  end

  def check_open_questions
    oqs = Array(@doc["open_questions"])
    return if oqs.empty?
    # A card with unresolved product/infra decisions is NOT-READY, regardless of
    # how the rest of the contract was modeled. The gate owns this, not the author.
    labels = oqs.map { |q| q.is_a?(Hash) ? (q["question"] || q.values.first) : q.to_s }
    v("open_questions unresolved (#{oqs.size}) — NOT-READY until answered: #{labels.join(' | ')}")
  end

  def fail_structure
    warn "MALFORMED: top-level YAML is not a mapping"
    exit 2
  end

  def report
    if @violations.empty?
      puts "DoR: PASSED — #{@doc['id']} #{@doc['title']}"
      exit 0
    else
      puts "DoR: NOT-READY — #{@doc['id']} #{@doc['title']} (#{@violations.size} gap(s))"
      @violations.each_with_index { |m, i| puts "  #{i + 1}. #{m}" }
      exit 1
    end
  end
end

require "set"
path = ARGV[0] or abort("usage: ruby dor_lint.rb <story.yaml>")
begin
  doc = YAML.safe_load(File.read(path), permitted_classes: [Symbol])
rescue => e
  warn "MALFORMED: #{e.message}"
  exit 2
end
Lint.new(doc).run
