import { useMemo, useState } from "react";
import {
  Modal,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  Switch,
  Platform,
  Keyboard,
  KeyboardAvoidingView,
  ScrollView,
  TouchableWithoutFeedback,
} from "react-native";
import { FontAwesome } from "@expo/vector-icons";

import { Colors, Fonts } from "@/constants/theme";

type Environment = "any" | "indoors" | "outdoors";

export type Filters = {
  capacity: number | null;
  environment: Environment;
  techEnhanced: boolean;
};

type Props = {
  value: Filters;
  onChange: (next: Filters) => void;
};

export function FilterBar({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<Filters>(value);

  const theme = Colors.light;

  const summary = useMemo(() => {
    const parts: string[] = [];
    if (value.capacity != null) parts.push(`${value.capacity}+ ppl`);
    if (value.environment !== "any") parts.push(value.environment);
    if (value.techEnhanced) parts.push("tech");
    return parts.length ? parts.join(" • ") : "Add Filters...";
  }, [value]);

  const openSheet = () => {
    setDraft(value);
    setOpen(true);
  };

  const closeSheet = () => setOpen(false);

  const apply = () => {
    onChange(draft);
    setOpen(false);
  };

  const clear = () => {
    const empty: Filters = { capacity: null, environment: "any", techEnhanced: false };
    setDraft(empty);
    onChange(empty);
  };

  return (
    <>
      {/* Fake search bar */}
      <Pressable
        onPress={openSheet}
        accessibilityRole="button"
        style={[styles.barShadow, { shadowColor: theme.shadow }]}
      >
        <View style={[styles.bar, { backgroundColor: theme.surfaceVariant }]}>
          <Text
            style={[
              styles.barText,
              { color: theme.text, fontFamily: Fonts.sans },
              summary === "Add Filters..." && styles.barPlaceholder,
            ]}
          >
            {summary}
          </Text>
          <FontAwesome name="filter" size={18} color={theme.brand} />
        </View>
      </Pressable>

      {/* Modal bottom sheet */}
      <Modal visible={open} animationType="slide" transparent onRequestClose={closeSheet}>
        {/* Backdrop closes modal */}
        <Pressable style={styles.backdrop} onPress={closeSheet} />

        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
            <View style={[styles.sheet, { backgroundColor: theme.surface }]}>
              {/*  Option A: true centered title + absolute close button */}
              <View style={styles.sheetHeader}>
                <Text
                  style={[
                    styles.sheetTitle,
                    { color: theme.text, fontFamily: Fonts.sans },
                  ]}
                >
                  Filters
                </Text>

                <Pressable
                  style={styles.closeButton}
                  onPress={() => {
                    Keyboard.dismiss();
                    closeSheet();
                  }}
                  hitSlop={12}
                >
                  <Text style={[styles.close, { color: theme.text }]}>✕</Text>
                </Pressable>
              </View>

              <ScrollView keyboardShouldPersistTaps="handled">
                {/* Capacity */}
                <View style={styles.row}>
                  <Text style={[styles.label, { color: theme.text, fontFamily: Fonts.sans }]}>
                    Capacity
                  </Text>
                  <TextInput
                    value={draft.capacity == null ? "" : String(draft.capacity)}
                    onChangeText={(t) => {
                      const n = parseInt(t.replace(/[^\d]/g, ""), 10);
                      setDraft((d) => ({ ...d, capacity: Number.isFinite(n) ? n : null }));
                    }}
                    placeholder="e.g. 4"
                    placeholderTextColor={theme.text}
                    keyboardType={Platform.OS === "ios" ? "number-pad" : "numeric"}
                    style={[
                      styles.input,
                      {
                        color: theme.text,
                        backgroundColor: theme.surface,
                        borderColor: theme.outline,
                        fontFamily: Fonts.mono,
                      },
                    ]}
                    returnKeyType="done"
                    onSubmitEditing={Keyboard.dismiss}
                  />
                </View>

                {/* Indoors / Outdoors */}
                <View style={styles.rowColumn}>
                  <Text style={[styles.label, { color: theme.text, fontFamily: Fonts.sans }]}>
                    Environment
                  </Text>

                  <View style={[styles.segment, { backgroundColor: theme.outlineSoft }]}>
                    <SegmentButton
                      label="Any"
                      active={draft.environment === "any"}
                      onPress={() => setDraft((d) => ({ ...d, environment: "any" }))}
                      theme={theme}
                    />
                    <SegmentButton
                      label="Indoors"
                      active={draft.environment === "indoors"}
                      onPress={() => setDraft((d) => ({ ...d, environment: "indoors" }))}
                      theme={theme}
                    />
                    <SegmentButton
                      label="Outdoors"
                      active={draft.environment === "outdoors"}
                      onPress={() => setDraft((d) => ({ ...d, environment: "outdoors" }))}
                      theme={theme}
                    />
                  </View>
                </View>

                {/* Tech Enhanced */}
                <View style={styles.row}>
                  <Text style={[styles.label, { color: theme.text, fontFamily: Fonts.sans }]}>
                    Tech Enhanced
                  </Text>
                  <Switch
                    value={draft.techEnhanced}
                    onValueChange={(v) => setDraft((d) => ({ ...d, techEnhanced: v }))}
                    trackColor={{ false: theme.outlineSoft, true: theme.brand }}
                    thumbColor={theme.surface}
                  />
                </View>

                {/* Actions */}
                <View style={styles.actions}>
                  <Pressable
                    onPress={() => {
                      Keyboard.dismiss();
                      clear();
                    }}
                    style={[
                      styles.btn,
                      styles.btnGhost,
                      { backgroundColor: theme.surface, borderColor: theme.outline },
                    ]}
                  >
                    <Text style={[styles.btnGhostText, { color: theme.text, fontFamily: Fonts.sans }]}>
                      Clear
                    </Text>
                  </Pressable>

                  <Pressable
                    onPress={() => {
                      Keyboard.dismiss();
                      apply();
                    }}
                    style={[styles.btn, styles.btnPrimary, { backgroundColor: theme.brand }]}
                  >
                    <Text
                      style={[
                        styles.btnPrimaryText,
                        { color: theme.textOnBrand, fontFamily: Fonts.sans },
                      ]}
                    >
                      Apply
                    </Text>
                  </Pressable>
                </View>
              </ScrollView>
            </View>
          </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
      </Modal>
    </>
  );
}

function SegmentButton({
  label,
  active,
  onPress,
  theme,
}: {
  label: string;
  active: boolean;
  onPress: () => void;
  theme: typeof Colors.light;
}) {
  return (
    <Pressable onPress={onPress} style={[styles.segBtn, active && { backgroundColor: theme.brand }]}>
      <Text
        style={[
          styles.segText,
          { fontFamily: Fonts.sans, color: theme.text },
          active && { color: theme.textOnBrand, opacity: 1 },
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  barShadow: {
    borderRadius: 22,
    shadowOpacity: 0.5,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
    elevation: 6,
    backgroundColor: "transparent",
  },

  bar: {
    height: 44,
    borderRadius: 22,
    overflow: "hidden",
    paddingHorizontal: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  barText: { fontSize: 15 },
  barPlaceholder: { opacity: 0.55 },

  backdrop: { flex: 1 },

  sheet: {
    padding: 16,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },

  //  Center title via header container, not by Text layout
  sheetHeader: {
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },

  sheetTitle: {
    fontSize: 18,
    fontWeight: "700",
    textAlign: "center",
  },

  //  Absolute close button so it doesn't affect centering
  closeButton: {
    position: "absolute",
    right: 0,
    top: 0,
  },

  close: { fontSize: 18, opacity: 0.8 },

  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 10,
  },

  rowColumn: {
    paddingVertical: 10,
    gap: 10,
  },

  label: { fontSize: 15, fontWeight: "600" },

  input: {
    width: 110,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 15,
    textAlign: "right",
  },

  segment: {
    flexDirection: "row",
    borderRadius: 14,
    padding: 4,
    gap: 6,
  },

  segBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: "center",
  },

  segText: { fontSize: 13, fontWeight: "600", opacity: 0.8 },

  actions: {
    flexDirection: "row",
    gap: 10,
    marginTop: 14,
    paddingBottom: 6,
  },

  btn: {
    flex: 1,
    height: 44,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },

  btnPrimary: {},
  btnPrimaryText: { fontWeight: "700" },

  btnGhost: {
    borderWidth: 1,
  },
  btnGhostText: { fontWeight: "700", opacity: 0.85 },
});
