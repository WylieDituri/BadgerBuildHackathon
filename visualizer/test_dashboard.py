#!/usr/bin/env python3
"""
Quick test to verify the dashboard fix works.
This simulates the update cycle without actually running the animation.
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def test_dynamic_patch_removal():
    """Test that we can properly remove dynamic patches."""
    print("🧪 Testing dynamic patch removal fix...")
    
    # Create a simple plot
    fig, ax = plt.subplots()
    
    # Add some static patches
    static_patch = mpatches.Circle((0.5, 0.5), 0.1, color='blue')
    ax.add_patch(static_patch)
    
    # Add some dynamic patches (marked with _dynamic attribute)
    dynamic_patch1 = mpatches.Circle((0.3, 0.3), 0.05, color='red')
    dynamic_patch1._dynamic = True
    ax.add_patch(dynamic_patch1)
    
    dynamic_patch2 = mpatches.Circle((0.7, 0.7), 0.05, color='red')
    dynamic_patch2._dynamic = True
    ax.add_patch(dynamic_patch2)
    
    print(f"   Initial patches count: {len(ax.patches)}")
    assert len(ax.patches) == 3, "Should have 3 patches initially"
    
    # Try the OLD way (this would cause the error)
    print("   Testing OLD method (would fail)...")
    try:
        # This is what was causing the error
        ax.patches = [p for p in ax.patches if not hasattr(p, '_dynamic')]
        print("   ❌ OLD method didn't fail (unexpected)")
        return False
    except AttributeError as e:
        print(f"   ✓ OLD method fails as expected: {e}")
    
    # Try the NEW way (the fix)
    print("   Testing NEW method (should work)...")
    try:
        for patch in list(ax.patches):
            if hasattr(patch, '_dynamic'):
                patch.remove()
        print(f"   ✓ NEW method works! Patches count: {len(ax.patches)}")
        assert len(ax.patches) == 1, "Should have only 1 static patch left"
        print("   ✓ Correct number of patches remaining")
        return True
    except Exception as e:
        print(f"   ❌ NEW method failed: {e}")
        return False
    finally:
        plt.close(fig)


def test_dashboard_import():
    """Test that the dashboard can be imported without errors."""
    print("\n🧪 Testing dashboard import...")
    try:
        from live_dashboard import LiveDashboard
        print("   ✓ Dashboard imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("🔧 Dashboard Fix Verification")
    print("="*60)
    
    tests = [
        ("Dynamic Patch Removal", test_dynamic_patch_removal),
        ("Dashboard Import", test_dashboard_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Results:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("🎉 All tests passed! The dashboard fix is working.")
        print("\n💡 Next steps:")
        print("   1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("   2. Start simulator: cd visualizer && python traffic_simulator.py")
        print("   3. Start dashboard: cd visualizer && python live_dashboard.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

